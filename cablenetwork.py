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

from neo4j import GraphDatabase
from mongodbhandler import CablegateDatabase

import re
from datetime import datetime

class CableNetwork(object):
    def __init__(self, config, overwrite=True, minoccs=1, mincoocs=1, maxcables=None, year=None):
        self.mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
        self.graphdb = GraphDatabase(config['general']['neo4j'])
        self.config = config
        nodecache = self.update_occurrences_network(overwrite, minoccs, mincoocs, maxcables, year)
        self.update_cooccurrences_network(nodecache, overwrite, minoccs, mincoocs, maxcables)

    def update_occurrences_network(self, overwrite=False, minoccs=1, mincoocs=1, maxcables=None, year=None):
        nodecache = {}
        count=0
        if maxcables is None:
            maxcables = self.mongodb.cables.count()
        if year is None:
            cable_curs = self.mongodb.cables.find(timeout=False)
        else:
            start = datetime(year,1,1,0,0,0)
            end = datetime(year+1,1,5,0,0,0)
            cable_curs = self.mongodb.cables.find({"start":{"$gte":start,"$lt":end}}, timeout=False)
        for cable in cable_curs:
            with self.graphdb.transaction as trans:
                del cable['content']
                cablenode = self.add_node(cable, trans)

                for ngid, occs in cable['edges']['NGram'].iteritems():
                    ngram = self.mongodb.ngrams.find_one({'_id':ngid})
                    if ngram is None:
                        logging.warning('ngram %s linked to document %s but not found in mongodb'%(ngid, cable['_id']))
                        continue
                    if ngram['occs'] < minoccs: continue
                    ### first time if export this node
                    if 'nodeid' not in ngram or str(ngram['nodeid']) not in nodecache:
                        new_ngramnode = self.add_node(ngram, trans)
                        ngram['nodeid'] = new_ngramnode.id
                        nodecache[str(new_ngramnode.id)] = new_ngramnode
                        self.mongodb.ngrams.save(ngram)
                    with self.graphdb.transaction:
                        cablenode.occurrence(nodecache[str(ngram['nodeid'])], weight=occs)

                logging.debug("done the network around cable %d"%cablenode.id)
                count += 1
                if count > maxcables: return nodecache
        return nodecache

    def update_cooccurrences_network(self, nodecache, overwrite=False, minoccs=1, mincoocs=1, maxcables=None):
        nodecachedkeys = [int(key) for key in nodecache.keys()]
        logging.debug("cooccurrences processing for %d ngram nodes"%len(nodecachedkeys))
        with self.graphdb.transaction:
            for ngram in self.mongodb.ngrams.find({'nodeid': {"$in": nodecachedkeys}}, timeout=False):
                # this REGEXP select only edges with source == ngram['_id']
                coocidRE = re.compile("^"+ngram['_id']+"_[a-z0-9]+$")
                for cooc in self.mongodb.cooc.find({"_id":{"$regex":coocidRE}, "value": { "$gte": mincoocs }}, timeout=False):
                    #if cooc['value'] < mincoocs: continue
                    ng1, ng2 = cooc['_id'].split("_")
                    if ng1 == ng2:
                        self.mongodb.cooc.delete({"_id":cooc['_id']})
                        continue
                    ngram2 = self.mongodb.ngrams.find_one({'_id':ng2})
                    if ngram2['nodeid'] == ngram['nodeid']:
                        logging.warning("not setting relationship on a node itself")
                        continue
                    if ngram2['nodeid'] not in nodecachedkeys:
                        #logging.warning("ngram not in nodecache keys, skipping")
                        continue
                    # inserting the cooccurrence
                    nodecache[str(ngram['nodeid'])].cooccurrence(nodecache[str(ngram2['nodeid'])], weight=cooc['value'])

    def set_node_attr(self, record, node):
        """
        Type conversion from python/mongodb to neo4j
        restricts a node's attributes to string or numeric
        """
        for key, value in record.iteritems():
            if type(value) == unicode:
                node[key.encode("ascii","ignore")] = value.encode("ascii","ignore")
            elif type(value) == int or type(value) == float or type(value) == str:
                node[key.encode("utf-8","replace")] = value
            elif type(value) == datetime:
                node[key.encode("utf-8","replace")] = value.strftime('%Y-%m-%d')

    def add_node(self, record, transact=None):
        if transact is None:
            with self.transaction:
                node = self.graphdb.node()
                self.set_node_attr(record, node)
                return node
        else:
            node = self.graphdb.node()
            self.set_node_attr(record, node)
            return node

    def get_node(self, _id):
        return self.graphdb.node[_id]
