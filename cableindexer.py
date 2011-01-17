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
        if overwrite is True and "ngrams" in self.storage.collection_names():
            self.storage.ngrams.remove()
        for cable in self.storage.cables.find(timeout=False):
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
                stemmer.Nltk()
            )
            self.update_cooccurrences(docngrams)
        neighbours_id = []
        #for cable in self.storage.cables.find():
        #    neighbours_id += [cable["_id"]]
        #    self.update_logJaccard(cable, overwrite)

    def update_cooccurrences(self, docngrams):
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

    def update_logJaccard( self, document, neighbours_id, overwrite=True ):
        """
        a Jaccard-like similarity distance
        Invalid if summing values avor many periods
        """
        doc1ngrams = document['edges']['NGrams'].keys()
        for docid in neighbours_id:
            document2 = self.storage.cables.find_one({"_id":docid})
            if docid != document['_id']:
                document2 = self.storage.cables.find_one({"_id":doc_id_2})
                doc2ngrams = self.documentngrams[docid]
                ngramsintersection = doc1ngrams & doc2ngrams
                ngramsunion = (doc1ngrams | doc2ngrams)
                weight = 0
                numerator = 0
                for ngi in ngramsintersection:
                    numerator += 1/(math.log( 1 + self.corpus['edges']['NGram'][ngi] ))
                denominator = 0
                for ngi in ngramsunion:
                    denominator += 1/(math.log( 1 + self.corpus['edges']['NGram'][ngi] ))
                if denominator > 0:
                    weight = numerator / denominator
                submatrix.set(document['id'], docid, value=weight, overwrite=True)
                submatrix.set(docid, document['id'], value=weight, overwrite=True)
        return submatrix

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
