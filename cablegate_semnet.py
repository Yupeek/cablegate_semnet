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

from optparse import OptionParser

import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

from cableimporter import CableImporter
from mongodbhandler import CablegateMongo
from datamodel import Cable, getNodeId, getNodeLabel, updateNodesEdges, NGram
from cablegateextractor import CableExtractor

import yaml

from tinasoft.pytextminer import tagger, filtering, stemmer, stopwords, tokenizer, corpus, whitelist

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-a", "--archive", dest="archive", help="cablegate archive path", metavar="FILE")
    parser.add_option("-o", "--occurrences", dest="minoccs", help="minimum keyphrase occurrence", metavar="int")
    parser.add_option("-c", "--config", dest="config", help="config yaml file path", metavar="FILE")
    (options, args) = parser.parse_args()
    print options, args
    
    config = yaml.safe_load( file( options.config, 'rU' ) )
    db = CablegateMongo("localhost")
    CableImporter(db["cables"], options.archive)