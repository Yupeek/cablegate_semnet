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
import pymongo
import re
from datetime import datetime

class CableNetwork(object):
    def __init__(self, config, graphtype, minoccs=1, maxcoocs=1, maxcables=None, year=None):
        self.mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
        self.graphdb = GraphDatabase(config['general']['neo4j'])
        self.config = config
        if graphtype is None or graphtype=="occurrences":
            self.update_occurrences_network(minoccs, maxcoocs, maxcables, year, documents=False)
        elif graphtype == "cooccurrences":
            nodecache, ngramcache = self.update_occurrences_network(minoccs, maxcoocs, maxcables, year, documents=False)
            self.update_cooccurrences_network(nodecache, ngramcache, minoccs, maxcoocs, maxcables)

    def update_occurrences_network(self, minoccs=1, maxcoocs=1, maxcables=None, year=None, documents=True):
        nodecache = {}
        ngramcache = {}
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
                if documents is True:
                    del cable['content']
                    cablenode = self.add_node(cable, trans)

                for ngid, occs in cable['edges']['NGram'].iteritems():
                    ngram = self.mongodb.ngrams.find_one({'_id':ngid})
                    if ngram is None:
                        #logging.warning('ngram %s linked to document %s but not found in mongodb'%(ngid, cable['_id']))
                        continue
                    if ngram['occs'] < minoccs: continue
                    ### first time if export this node
                    if ngid not in ngramcache.keys():
                        new_ngramnode = self.add_node(ngram, trans)
                        ngramcache[ngid] = str(new_ngramnode.id)
                        nodecache[str(new_ngramnode.id)] = new_ngramnode
                    if documents is True:
                        cablenode.occurrence(ngramcache[ngid], weight=occs)
                logging.debug("done the network around cable %s"%cable["_id"])
                count += 1
                if count > maxcables: return nodecache
        return nodecache, ngramcache

    def update_cooccurrences_network(self, nodecache, ngramcache, minoccs=1, maxcoocs=1, maxcables=None):
        logging.debug("cooccurrences processing for %d ngram nodes"%self.mongodb.ngrams.find({'_id': {"$in": ngramcache.keys()}}, timeout=False).count())
        with self.graphdb.transaction as trans:
            for ngram in self.mongodb.ngrams.find({'_id': {"$in": ngramcache.keys()}}, timeout=False):
                # this REGEXP select only edges with source == ngram['_id']
                coocidRE = re.compile("^"+ngram['_id']+"_[a-z0-9]+$")
                for cooc in self.mongodb.cooc.find({"_id":{"$regex":coocidRE}}, sort=[("value",pymongo.DESCENDING)], limit=maxcoocs, timeout=False):
                    ng1, ng2 = cooc['_id'].split("_")
                    if ng1 == ng2:
                        self.mongodb.cooc.delete({"_id":cooc['_id']})
                        continue
                    ngram2 = self.mongodb.ngrams.find_one({'_id':ng2})
                    if ngramcache[ngram2['_id']] == ngramcache[ngram['_id']]:
                        logging.warning("not setting relationship on a node itself")
                        continue
                    if ngramcache[ngram['_id']] not in nodecache.keys():
                        continue
                    # write the cooccurrence
                    nodecache[ngramcache[ngram['_id']]].cooccurrence(
                        nodecache[ngramcache[ngram2['_id']]],
                        weight=cooc['value']
                    )

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
