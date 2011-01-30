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
from cableextractor import CableExtract
from cablenetwork import CableNetwork
import yaml

def get_parser():
    parser = OptionParser()
    parser.add_option("-e", "--execute", dest="execute", help="execution action")
    parser.add_option("-a", "--archive", dest="archive", help="cablegate archive path")
    parser.add_option("-m", "--minoccurrences", dest="minoccs", help="minimum keyphrases' occurrences", type="int")
    parser.add_option("-n", "--mincooccurrences", dest="mincoocs", help="minimum keyphrases' cooccurrences", type="int")
    parser.add_option("-c", "--config", dest="config", help="config yaml file path", metavar="FILE")
    parser.add_option("-o", "--overwrite", dest="overwrite", help="overwrite database contents", type="int")
    parser.add_option("-p", "--path", dest="path", help="output path file path", metavar="FILE")
    parser.usage = "bad parameters"
    return parser

if __name__ == "__main__":
    parser = get_parser()
    (options, args) = parser.parse_args()
    print options, args

    config = yaml.safe_load( file( options.config, 'rU' ) )

    if options.execute == 'import':
        importer = CableImporter( config, options.archive, bool(options.overwrite) )
    elif options.execute == 'extract':
        extractor = CableExtract( config, bool(options.overwrite) )
    elif options.execute == 'network':
        extractor = CableNetwork( config, bool(options.overwrite), options.minoccs, options.mincoocs )
    else:
        print parser.usage
