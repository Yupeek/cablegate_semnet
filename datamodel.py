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

def addUniqueEdge( node, type, key, value ):
    """
    low level method writing ONLY ONCE a weighted edge
    """
    if 'edges' not in node:
        node['edges']={}
    if type not in node['edges']:
        node['edges'][type]={}
    if key in node['edges'][type]:
        return node
    else:
        node['edges'][type][key] = value
        return node

def overwriteEdge( node, type, key, value ):
    """
    low level method overwriting a weighted edge
    """
    if 'edges' not in node:
        node['edges']={}
    if type not in node['edges']:
        node['edges'][type]={}
    node['edges'][type][key] = value
    return node

def addEdge( node, type, key, value ):
    """
    low level method incrementing a weighted edge
    """
    if 'edges' not in node:
        node['edges']={}
    if type not in node['edges']:
        node['edges'][type]={}
    if key in node['edges'][type]:
        node['edges'][type][key] += value
    else:
        node['edges'][type][key] = value
    return node

def initEdges(node):
    if 'edges' not in node:
        node['edges']={}
    node["edges"]['NGram'] = {}
    node["edges"]['Document'] = {}
    return node
