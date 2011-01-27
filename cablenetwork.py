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

import httplib2
DEBUG = 1


class CableNetwork(object):
    """
    Reads all mongodb's cables to produce a network into neo4j
    """
    def __init__(self, config):
        self.config = config
        self.mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
        self.graphdb = GraphDatabase(config['general']['neo4j'])
        self.update_network()

    def _set_node_attr(self, record, node):
        """
        Type conversion from python/mongodb to neo4j
        """
        for key, value in record.items():
            if type(value)=='unicode':
                node.set(key, value.encode("utf_8","ignore"))
            elif type(value) in ['int','float','str']:
                node.set(key, value)
            elif type(value)=='datetime':
                node.set(key, value.strftime('%Y-%m-%d'))

    def update_network(self):
        for cable in self.mongodb.cables.find(timeout=False, limit=100):
            cablenode = self.graphdb.nodes.create()
            self._set_node_attr(cable, cablenode)
            for ng, occs in cable['edges']['NGram'].items():
                ngram = self.mongodb.ngrams.find_one({"_id":ng})
                ngramnode = self.graphdb.nodes.create()
                self._set_node_attr(ngram, ngramnode)
                cablenode.relationships.create("occurence", ngramnode, weight=occs)

            logging.debug( "done Cable %s"%cablenode.id )
