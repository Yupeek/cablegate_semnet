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

import itertools

class CableNetwork(object):
    """
    Reads all mongodb's cables to produce a network into neo4j
    """
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config
        self.graphdb = GraphDatabase("http://localhost:7474/db/data/")

    def update_cooccurrences(self):
        for cable in self.storage.cables.find(timeout=False,limit=10):
            cablenode = self.graphdb.node(**cable)
            for (ngi, ngj) in itertools.combinations(cable['edges']['NGram'], 2):
                ngrami = self.storage.ngrams.find_one({"_id":ngi})
                ngramj = self.storage.ngrams.find_one({"_id":ngj})
                n1 = self.graphdb.node(**ngrami)
                n2 = self.graphdb.node(**ngramj)
                n1.relationships.create("cooccurrences", n2, weight=1)
