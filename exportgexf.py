# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2011 Elias Showk
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

__author__="elishowk@nonutc.fr"

# Tenjin, the fastest template engine in the world !
import tenjin
from tenjin.helpers import *

import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")


class GexfExporter(object):
    """
    A Gexf Exporter engine providing multipartite graph exports
    """
    def __init__(self, storage, config, path, minoccs, mincoocs, **kwargs):
        """
        ignoring path but loading options and tenjin Engine
        """
        engine = tenjin.Engine()
        graph = {
            'storage': storage,
            'minoccs': minoccs,
            'mincoocs': mincoocs
        }
        graph.update(kwargs)
        open(path, 'w+b').write(
            engine.render(config['graph']['template'], graph)
        )
