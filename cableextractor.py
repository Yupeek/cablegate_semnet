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

import re
import itertools

import cPickle
from nltk import PorterStemmer

from mongodbhandler import CablegateDatabase

from cabletokenizer import NGramizer
from datamodel import initEdges, addEdge
import filtering
from multiprocessing import pool

#class CableExtract(object):
#    """
#    Reads all database entries to :
#    - extract and filter NGrams from content
#    - write the Document-NGram network
#    """
#    def __init__(self, config, overwrite=True, maxcables=None):
#        self.mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
#        self.config = config
#        filters = self._get_extraction_filters()
#        postagger = cPickle.load(open(self.config['extraction']['tagger'],"r"))
#
#        if overwrite is True and "ngrams" in self.mongodb.collection_names():
#            self.mongodb.drop_collection("ngrams")
#
#        if overwrite is True and "cooc" in self.mongodb.collection_names():
#            self.mongodb.drop_collection("cooc")
#
#        extract_gen = self.extract(NGramizer(self.config), filters, postagger, overwrite, maxcables)
#        try:
#            while 1:
#                cable = extract_gen.next()
#                self.update_cable_cooc(cable)
#        except StopIteration, si:
#            return

def worker(config, cable, filters, postagger, overwrite):
    mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
    if overwrite is True:
        cable = initEdges(cable)
    # extract and filter ngrams
    ngramizer = NGramizer(config)
    ngramizer.extract(
        cable,
        filters,
        postagger,
        PorterStemmer()
    )
    update_cable_cooc(cable, mongodb)
    mongodb.cables.update(
        {"_id":cable['_id']},
        {"$set":{"edges": cable['edges']}})


def update_cable_cooc(cable, mongodb):
    for ng1, ng2 in itertools.combinations(cable['edges']['NGram'].keys(), 2):
        coocid12 = ng1+"_"+ng2
        #cooc12 = self.mongodb.cooc.find_one({'_id': coocid12})
        if mongodb.cooc.find_one({'_id': coocid12}) is None:
            coocid21 = ng2+"_"+ng1
            #cooc21 = self.mongodb.cooc.find_one({'_id': coocid21})
            if mongodb.cooc.find_one({'_id': coocid21}) is None:
                # none exist : creates one
                cooc12 = { '_id': coocid12, 'value': 1 }
                mongodb.cooc.save(cooc12)
                continue
            else:
                mongodb.cooc.update(
                    {'_id': coocid21},
                    {"$inc":{"value": 1}})
                continue
        else:
            mongodb.cooc.update(
                {'_id': coocid12},
                {"$inc":{"value": 1}})
            continue


def extract(config, overwrite=True, maxcables=None):
    """
    gets the all cables from storage then extract ngrams and produce networks edges and weights
    """
    mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
    filters = _get_extraction_filters(config)
    postagger = cPickle.load(open(config['extraction']['tagger'],"r"))

    if overwrite is True and "ngrams" in mongodb.collection_names():
        mongodb.drop_collection("ngrams")

    if overwrite is True and "cooc" in mongodb.collection_names():
        mongodb.drop_collection("cooc")

    count=0
    if maxcables is None:
        maxcables = mongodb.cables.count()
    extractionpool = pool.Pool(processes=config['general']['processes'])
    for cable in mongodb.cables.find(timeout=False):
        extractionpool.apply_async(worker, (config, cable, filters, postagger, overwrite))
        count+=1
        logging.debug("extracting %d cables topics"%count)
        if count>=maxcables: break
    extractionpool.close()
    extractionpool.join()

def _get_extraction_filters(config):
    """
    returns extraction filters
    """
    filters = [filtering.WordSizeFilter(
        config = {
            'rules': {
                'minWordSize': config['extraction']['minWordSize']
            }
        }
    )]
    filters += [filtering.PosTagValid(
        config = {
            'rules': re.compile(config['extraction']['postag_valid'])
        }
    )]
    return filters
