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

from os.path import join
import re

from cabletokenizer import NGramizer

from tinasoft.pytextminer import stopwords, filtering, tagger, stemmer

class CableExtractor(object):
    """
    Reads all database entries to produce a network
    usage :
      extractor = Exporter(minoccs=2)
    """
    def __init__(self, storage, config, minoccs=1):
        self.storage = storage
        self.config = config
        filters = self._get_extraction_filters()
        # instanciate the tagger, takes times if learning
        postagger = tagger.TreeBankPosTagger(
            training_corpus_size = 10000,
            trained_pickle = self.config['extraction']['tagger']
        )
        self.storage.ngrams.remove()
        self.index_cables(NGramizer(self.storage, self.config['extraction']), filters, postagger, minoccs)
      
    def index_cables(self, ngramizer, filters, postagger, minoccs):
        """
        gets the a document from storage then extract n-grams
        """
        for cable in self.storage.cables.find():
            if cable is None:
                logging.warning("cable %d not founf in the database, skipping"%cable_id)
            # extract and filter ngrams
            docngrams = ngramizer.extract(
                cable,
                filters,
                postagger,
                stemmer.Nltk()
            )

        logging.info("CableExtractor.extract_cables is done")

    
    def _get_extraction_filters(self):
      """
      returns extraction filters
      """
      filters = [filtering.PosTagValid(
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