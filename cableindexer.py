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

from cabletokenizer import NGramizer
from datamodel import initEdges, addEdge
from tinasoft.pytextminer import stopwords, filtering, tagger, stemmer

class CableIndexer(object):
    """
    Reads all database entries to produce a network
    usage :
      extractor = Exporter(minoccs=2)
    """
    def __init__(self, storage, config, overwrite=True):
        self.storage = storage
        self.config = config
        filters = self._get_extraction_filters()
        # instanciate the tagger, takes times if learning
        postagger = tagger.TreeBankPosTagger(
            training_corpus_size = 10000,
            trained_pickle = self.config['extraction']['tagger']
        )
        self.cable_semnet(NGramizer(self.storage, self.config['extraction']), filters, postagger, overwrite)

    def cable_semnet(self, ngramizer, filters, postagger, overwrite):
        """
        gets the all cables from storage then extract n-grams and produce networks edges and weights
        """
        #if overwrite is True and "ngrams" in self.storage.collection_names():
        #    self.storage.ngrams.remove()
        #for cable in self.storage.cables.find(timeout=False):
        #    if cable is None:
        #        logging.warning("cable %d not found in the database, skipping"%cable_id)
        #        continue
        #    if overwrite is True:
        #        cable = initEdges(cable)
        #    # extract and filter ngrams
        #    docngrams = ngramizer.extract(
        #        cable,
        #        filters,
        #        postagger,
        #        stemmer.Nltk()
        #    )
        #    self.update_cooccurrences(docngrams)
        if overwrite is True:
            for cable in self.storage.cables.find():
                cable['edges']['Document']={}
        neighbours_id = []
        counter=0
        for cable in self.storage.cables.find(timeout=False):
            neighbours_id += [cable["_id"]]
            self.update_logJaccard(cable, neighbours_id)
            counter += 1
            logging.debug("updated logJaccard edges from cable %s, done = %d"%(cable["_id"],counter))

    def update_cooccurrences(self, docngrams, minoccs=2):
        """ updates a document's ngrams cooccurrences """
        for (ngi, ngj) in itertools.combinations(docngrams, 2):

            ngram = self.storage.ngrams.find_one({"_id":ngi})
            if ngram is not None:
                ngram = addEdge( ngram, 'NGram', ngj, 1)
            self.storage.ngrams.save(ngram)

            ngram = self.storage.ngrams.find_one({"_id":ngj})
            if ngram is not None:
                ngram = addEdge( ngram, 'NGram', ngi, 1)
            self.storage.ngrams.save(ngram)

        logging.info("CableExtractor.update_cooccurrences done")

    def update_logJaccard(self, document, neighbours_id, minoccs=2):
        """
        a Jaccard-like similarity distance
        TODO : describe it !
        """
        doc1ngrams = document['edges']['NGram'].keys()
        for docid in neighbours_id:
            document2 = self.storage.cables.find_one({"_id":docid})
            if docid != document['_id']:
                document2 = self.storage.cables.find_one({"_id":docid})
                doc2ngrams = document2['edges']['NGram'].keys()
                #ngramsintersection = doc1ngrams & doc2ngrams
                #ngramsunion = (doc1ngrams | doc2ngrams)
                ngramsunion = []
                weight = 0
                numerator = 0
                denominator = 0
                for ng1 in doc1ngrams:
                    ngram = self.storage.ngrams.find_one({"_id":ng1})
                    if ngram is not None:
                        ngramOccs = len(ngram['edges']['Document'].keys())
                        if ng1 in doc2ngrams:
                            numerator += 1/(math.log( 1 + ngramOccs ))
                        denominator += 1/(math.log( 1 + ngramOccs ))
                        ngramsunion.append(ng1)
                for ng2 in doc2ngrams:
                    if ng2 not in ngramsunion:
                        ngram = self.storage.ngrams.find_one({"_id":ng2})
                        if ngram is not None:
                            ngramOccs = len(ngram['edges']['Document'].keys())
                            denominator += 1/(math.log( 1 + ngramOccs ))
                if denominator > 0:
                    weight = numerator/denominator
                if weight > 0:
                    self.storage.cables.save( addEdge( document, 'Document', docid, weight) )
                    self.storage.cables.save( addEdge( document2, 'Document', document['_id'], weight) )

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
