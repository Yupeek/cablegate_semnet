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

class CoocNetwork(object):
    """
    Reads all database entries to produce a network
    """
    def __init__(self, storage, config, mincoocs=1):
        self.storage = storage
        self.config = config
        self.cooc_map_reduce(mincoocs)
      
    def cooc_map_reduce(self, mincoocs):
        """
        execute a map-reduce operation on mongodb documents to produce the coocurrence edges matrix
        """
        result = self.storage.cables.map_reduce( self.get_mapper(), self.get_reducer(), out="cooccurrences", verbose="true" )
        logging.info("CableExtractor.map_reduce is done : %d result produced"%result.count())
        return result

    def get_mapper(self):   
        return code.Code(
            "function() {"
            "    for (var ngramid in this.edges.NGram) {"
            "        var coocslice = {};"
            "        for (var neighbourid in this.edges.NGram[ngramid]) {"
            "            if (neighbourid != ngramid) {"
            "                coocslice[neighbourid] = 1;"
            "            }"
            "        }"
            "        emit(ngramid, coocslice);"
            "    }"
            "}"
        )
        
    def get_reducer(self):
        return code.Code(
            "function(ngramid, coocslices) {"
            "    totalcooc = {};"
            "    for ( var slice in coocslices ) {"
            "        for ( var neighbourid in slice ) {"
            "            if ( neighbourid in totalcooc )"
            "                totalcooc[neighbourid] += slice[neighbourid];"
            "            else"
            "                totalcooc[neighbourid] = slice[neighbourid];"
            "        }"   
            "    }"
            "    return totalcooc;"
            "}"
        )