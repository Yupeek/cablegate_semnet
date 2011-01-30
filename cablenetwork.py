# -*- coding: utf-8 -*-
#  Copyright (C) 2010 elishowk@nonutc.fr
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

import neo4jrestclient.client
#neo4jrestclient.client.DEBUG=1
from neo4jrestclient.client import GraphDatabase, NotFoundError
from mongodbhandler import CablegateDatabase

from datetime import datetime

def updateEdge(graphdb, nodesourceid, nodetargetsid, type, value=1):
    nodesource = graphdb.nodes.get(nodesourceid)
    countnew=0
    countincrement=0
    edges_list = nodesource.relationships.all(types=[type])
    known_targets_id=[]
    # increments existing edges and append node id to a list
    for edge in edges_list:
        try:
            target_id = edge._get_end().id
            if target_id in nodetargetsid:
                known_targets_id += [target_id]
                edge['weight'] += value
                countincrement+=1
        except NotFoundError, notfound:
            logging.warning("error incrementing existing edge : %s"%notfound)
    # creates new edges
    new_targets_id = [targetid for targetid in nodetargetsid if targetid not in known_targets_id]
    for new_target_id in new_targets_id:
        if new_target_id != nodesourceid:
            nodetarget = graphdb.nodes.get(new_target_id)
            if nodetarget is None:
                logging.warning("cannot get node %d from graphdb"%new_target_id)
                continue
            nodesource.relationships.create(type, nodetarget, weight=value)
            countnew+=1
    logging.debug("created %d new edges and incremented %d on node %d"%(countnew, countincrement, nodesource.id))

def set_node_attr(record, node):
    """
    Type conversion from python/mongodb to neo4j
    restricts a node's attributes to string or numeric
    """
    for key, value in record.items():
        if type(value)==unicode:
            node.set(str(key), value.encode("utf_8","replace"))
        elif type(value) in [int,float,str]:
            node.set(str(key), value)
        elif type(value)==datetime:
            node.set(str(key), value.strftime('%Y-%m-%d'))

def add_node(graphdb, record):
    node = graphdb.nodes.create()
    set_node_attr(record, node)
    #logging.debug("created a new node with record %s"%record)
    return node

def get_node(graphdb, _id):
    try:
        return graphdb.nodes.get(_id)
    except NotFoundError:
        return None

class CableNetwork(object):
    """
    Reads all mongodb's cables to produce a network into neo4j
    """
    def __init__(self, config):
        self.config = config
        self.mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
        self.graphdb = GraphDatabase(config['general']['neo4j'])
        self.rootnode = self.graphdb.nodes.get(0)
        #self.empty_network()
        #self.empty_index()
        #self.create_network()
        self.process_cooccurrences()

    #def empty_index(self):
    #    for cable in self.mongodb.cables.find(timeout=False):
    #        self.graphdb.index(key='_id', value=cable['_id'], delete=True)
    #    for ngram in self.mongodb.ngrams.find(timeout=False):
    #        self.graphdb.index(key='_id', value=ngram['_id'], delete=True)

    #def empty_network(self):
    #    for rel in self.rootnode.relationships.outgoing(types=["cablegate"]):
    #        targetnode = rel.end
    #        self.graphdb.delete(rel)
    #        self.graphdb.delete(targetnode)

    def _set_node_attr(self, record, node):
        """
        Type conversion from python/mongodb to neo4j
        restricts a node's attributes to string or numeric
        """
        for key, value in record.items():
            if type(value)==unicode:
                node.set(str(key), value.encode("utf_8","replace"))
            elif type(value) in [int,float,str]:
                node.set(str(key), value)
            elif type(value)==datetime:
                node.set(str(key), value.strftime('%Y-%m-%d'))

    def _add_node(self, record):
        node = self.graphdb.nodes.create()
        self._set_node_attr(record, node)
        #node.index(key='_id', value=record['_id'], create=True)
        self.nodeindex[record['_id']] = node
        self.rootnode.relationships.create("cablegate", node)
        return node

    def _get_node(self, record_id):
        if record_id in self.nodeindex:
            return self.graphdb.nodes.get(self.nodeindex[record_id])
        else:
            None
        #nodes = self.graphdb.index(key='_id', value=record_id)
        #print "nodes indexed with the id %s"%record_id
        #print nodes
        #if len(nodes.keys()) == 0:
        #    return None
        #else:
        #    for node in nodes.values():
        #        return node

    def create_network(self, minoccs=1):
        """
        """
        nodeindex = {}
        for ngram in self.mongodb.ngrams.find(timeout=False):
            nodeindex[ngram['_id']] = self._add_node(ngram)
        logging.debug("inserted %d NGram nodes"%len(self.nodeindex.keys()))
        self.process_cooccurrences(nodeindex)

    def process_cooccurrences(self, ngram_index):
        #ngram_index = self._get_ngram_index()
        for cable in self.mongodb.cables.find(timeout=False):
            cablenode = self._add_node(cable)
            # cache for cooccurrences
            docngrams = cable['edges']['NGram'].keys()
            for ngid in cable['edges']['NGram'].keys():
                occs = cable['edges']['NGram'][ngid]
                ngramnode = ngram_index[ngid]
                cablenode.relationships.create("occurrence", ngramnode, weight=occs)
                for neighbour_id in docngrams:
                    if neighbour_id == ngid: continue
                    coocs = ngramnode.relationships.all(types=["cooccurrence"])

            logging.debug("done Cable %s"%cablenode.id)

    def _get_ngram_index(self):
        ngram_index = {}
        rootnode = self.graphdb.nodes.get(0)
        for edge in rootnode.traverse(
            types=['cablegate'],
            order=neo4jrestclient.client.BREADTH_FIRST,
            stop=neo4jrestclient.client.STOP_AT_DEPTH_ONE,
            uniqueness=neo4jrestclient.client.NODE,
            returns=neo4jrestclient.client.NODE
            ):
            #if edge.type!="cablegate": continue
            node = edge.end
            if node['category']=="NGram":
                ngram_index[node['_id']]=node
            else:
                # HACK to remove
                node.delete()
            print len(ngram_index.keys())
        return ngram_index
