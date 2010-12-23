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
import re
from UserDict import UserDict

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
  
def updateNodeEdges(updateedges, toupdate):
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
    convert = getNodeLabel(tokens).lower() 
    return sha256( convert.encode( 'ascii', 'replace' ) ).hexdigest()
  
class NetworkNode(UserDict):
    """
    is a the parent class
    """
    defaults = {
        'label': None,
        'content': None,
        'id': None,
        'edges': { 'Document' : {}, 'NGram' : {} }
    }
    
    def __init__(self, attributes=None, **kwargs):
        self.defaults.update(attributes)
        UserDict.__init__(self, self.defaults, **kwargs)
        
    def _addUniqueEdge( self, type, key, value ):
        """
        low level method writing ONLY ONCE a weighted edge 
        """
        if type not in self['edges']:
            self['edges'][type]={}
        if key in self['edges'][type]:
            return
        else:
            self['edges'][type][key] = value
            return

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
        return


class Cable(NetworkNode):
    
    def __init__(self, dict=None, **kwargs): 
        NetworkNode.__init__(self, dict, **kwargs)
        
    def _parseLabel(self):
        """
        TODO
        """
        #res = re.search(r"SUBJECT:(.+)\&\#x000A\;\&\#x000A;", self['content'], re.I|re.M)
        #if res is None: return
        #findlabel = res.group(0)
        #if findlabel is None: return
        #self['label'] = findlabel
        return
    
    def addEdge(self, type, key, value):
      if type in ["NGram"]:
          return self._addUniqueEdge( type, key, value )
      elif type in ["Document"]:
          return self._overwriteEdge( type, key, value )
      else:
          return self._addEdge( type, key, value )


class NGram(NetworkNode):
    """
    accepts only once to write an edge to a Document
    all other edges accept multiples writes
    """
    def __init__(self, dict=None, **kwargs): 
        NetworkNode.__init__(self, dict, **kwargs)
        self['edges'].update({'postag': {}, 'label': {}})
      
    def addEdge(self, type, key, value):
        if type in ["Document"]:
            return self._addUniqueEdge( type, key, value )
        elif type in ["NGram", "postag"]:
            return self._overwriteEdge( type, key, value )
        else:
            return self._addEdge( type, key, value )