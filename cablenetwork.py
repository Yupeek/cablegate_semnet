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

from pymongo import code

class CableNetwork(object):
    """
    Reads all database entries to produce a network
    """
    def __init__(self, storage, config, minoccs=1, mincoocs=1):
        self.storage = storage
        self.config = config
        # TODO : remove ngram occurring less than minoccs
        self.cooc_map_reduce(mincoocs)
        # TODO logJaccard mapreduce
      
    def cooc_map_reduce(self, mincoocs):
        """
        execute a map-reduce operation on mongodb documents to produce the coocurrence network
        """
        result = self.storage.cables.map_reduce( self.get_cooc_mapper(), self.get_cooc_reducer(), out="cooccurrences", verbose="true" )
        # TODO filtering cooc less than mincoocs
        logging.info("CableExtractor.map_reduce is done : %d result produced"%result.count())
        return result

    def get_cooc_mapper(self):   
        return code.Code(open("coocmapper.js",'rU').read())
        
    def get_cooc_reducer(self):
        return code.Code(open("coocreducer.js",'rU').read())