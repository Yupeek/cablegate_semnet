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
from hashlib import sha256
from uuid import uuid4
import re

import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

def getNodeLabel(tokens):
    """
     method forming clean unicode labels from token list
    """
    label = " ".join(tokens)
    if not isinstance(label, unicode):
        return unicode(label , "utf_8", errors='ignore')
    else:
        return label
  
def updateNodesEdges(updateedges, toupdate):
    """
    increments an object's edges with the candidate object's edges
    """
    for targettype in updateedges.iterkeys():
        for targetid, weight in updateedges[targettype].iteritems():
            toupdate.addEdge( targettype, targetid, weight )
    return toupdate
  
def getNodeId(tokens):
    """
    Common method constructing an ID str for all GraphNode objects
    """
    if type(content) == list:
        convert = getNodeLabel(content)
        return sha256( convert.encode( 'ascii', 'replace' ) ).hexdigest()
    else:
        return uuid4().hex
  
class GraphNode(dict):
    """
    GraphNode class
    is a the parent class of all the graph nodes classes
    """
    
    edges =  { 'Document' : {}, 'NGram' : {}, 'Corpus': {}, 'Whitelist': {} }
    label = None
    content = None
    id = None
    
    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        #if self.label is None or self.content is None or self.id is None:
        #    raise RuntimeError("incomplete %s class initialization"%self.__class__.__name__)
        
    def _addUniqueEdge( self, type, key, value ):
        """
        low level method writing ONLY ONCE a weighted edge 
        """
        if type not in self['edges']:
            self['edges'][type]={}
        if key in self['edges'][type]:
            return False
        else:
            self['edges'][type][key] = value
            return Trues

    def _overwriteEdge(self, type, key, value):
        """
        low level method overwriting a weighted edge 
        """
        if type not in self['edges']:
            self['edges'][type]={}
        self['edges'][type][key] = value

    def _addEdge(self, type, key, value):
        """
        low level method incrementing a weighted edge
        """
        if type not in self['edges']:
            self['edges'][type]={}
        if key in self['edges'][type]:
            self['edges'][type][key] += value
        else:
            self['edges'][type][key] = value
        return True

    def __getitem__(self, key):
        """
        compatibility with the dict class
        """
        return getattr( self, key, None )

    def __setitem__(self, key, value):
        """
        compatibility with the dict class
        """
        setattr( self, key, value )

    def __delitem__(self, key):
        """
        compatibility with the dict class
        """
        delattr(self, key)

    def __contains__(self, key):
        """
        compatibility with the dict class
        """
        try:
            getattr(self, key, None)
            return True
        except AttributeError, a:
            return False

class Cable(GraphNode):
    
    raw = ""
    
    def __init__(self, *args, **kwargs): 
        GraphNode.__init__(self, *args, **kwargs)
        
    def _parseLabel(self):
        #res = re.search(r"SUBJECT:(.+)\&\#x000A\;\&\#x000A;", self.content, re.I|re.M)
        #if res is None: return
        #findlabel = res.group(0)
        #if findlabel is None: return
        #self.label = findlabel
        return
    
    def addEdge(self, type, key, value):
      if type in ["NGram"]:
          return self._addUniqueEdge( type, key, value )
      elif type in ["Document"]:
          return self._overwriteEdge( type, key, value )
      else:
          return self._addEdge( type, key, value )


class NGram(GraphNode):
    """
    accepts only once to write an edge to a Document
    all other edges accept multiples writes
    """
    def __init__(self, *args, **kwargs):
        GraphNode.__init__(self, *args, **kwargs)
        self.edges.update({'postag': {}, 'forms': {}})
      
    def addEdge(self, type, key, value):
        if type in ["Document"]:
            return self._addUniqueEdge( type, key, value )
        elif type in ["NGram", "postag"]:
            return self._overwriteEdge( type, key, value )
        else:
            return self._addEdge( type, key, value )