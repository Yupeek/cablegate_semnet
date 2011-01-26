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

import math
from os.path import join
import re
import itertools
import nltk
import cPickle
from nltk import PorterStemmer

from cabletokenizer import NGramizer
from datamodel import initEdges, addEdge
import filtering
import stopwords

class CableExtract(object):
    """
    Reads all database entries to write the network
    """
    def __init__(self, storage, config, overwrite=True):
        self.storage = storage
        self.config = config
        filters = self._get_extraction_filters()
        # instanciate the tagger, takes times if learning
        postagger = cPickle.load(open(self.config['extraction']['tagger'],"r"))
        self.extract(NGramizer(self.storage, self.config['extraction']), filters, postagger, overwrite, limit)

    def extract(self, ngramizer, filters, postagger, overwrite, limit=None):
        """
        gets the all cables from storage then extract n-grams and produce networks edges and weights
        """
        if overwrite is True and "ngrams" in self.storage.collection_names():
            self.storage.ngrams.remove()

        for cable in self.storage.cables.find(timeout=False,limit=10):
            if cable is None:
                logging.warning("cable %d not found in the database, skipping"%cable_id)
                continue
            if overwrite is True:
                cable = initEdges(cable)
            # extract and filter ngrams
            docngrams = ngramizer.extract(
                cable,
                filters,
                postagger,
                PorterStemmer()
            )

    def _get_extraction_filters(self):
        """
        returns extraction filters
        """
        filters = [filtering.WordSizeFilter(
            config = {
                'rules': {
                    'minWordSize': self.config['extraction']['minWordSize']
                }
            }
        )]
        filters += [filtering.PosTagValid(
            config = {
                'rules': re.compile(self.config['extraction']['postag_valid'])
            }
        )]
        filters += [stopwords.StopWords(
            "file://%s"%join(
                self.config['general']['basedirectory'],
                self.config['general']['shared'],
                self.config['extraction']['stopwords']
            )
        )]
        return filters
