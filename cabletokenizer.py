# -*- coding: utf-8 -*-
#  Copyright (C) 2009-2011 CREA Lab, CNRS/Ecole Polytechnique UMR 7656 (Fr)
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

import nltk
import re
import string

from tinasoft.pytextminer import tagger
from tinasoft.pytextminer import filtering

from datamodel import NGram, getNodeId, getNodeLabel, updateNodeEdges   

import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

nltk_treebank_tokenizer = nltk.TreebankWordTokenizer()

# We consider following rules to apply whatever be the langage.
# ... is an ellipsis, put spaces around before splitting on spaces
# (make it a token)
ellipfind_re = re.compile(ur"(\.\.\.)", re.IGNORECASE|re.VERBOSE)
ellipfind_subst = ur" ... "
# A regexp to put spaces if missing after alone marks.
punct1find_re = re.compile(ur"(["+string.punctuation+"])([^ ])", re.IGNORECASE|re.VERBOSE)
punct1find_subst = ur"\1 \2"
# A regexp to put spaces if missing before alone marks.
punct2find_re = re.compile(ur"([^ ])([["+string.punctuation+"])", re.IGNORECASE|re.VERBOSE)
punct2find_subst = ur"\1 \2"


class NGramizer(object):
    """
    A tokenizer that divides a text into sentences
    then cleans the punctuation
    before tokenizing using nltk.TreebankWordTokenizer()
    """
    def __init__(self, storage):
        self.storage = storage
    
    def extract(self, doc, config, filters, tagger, stemmer):
        """
        sanitizes content and label texts
        tokenizes it
        POS tags the tokens
        constructs the resulting NGram objects
        """
        ngramMin = config['ngramMin']
        ngramMax = config['ngramMax']

        sentenceTaggedTokens = self.tokenize(
            self.sanitize(
                self.selectcontent(config, doc)
            ),
            tagger
        )
        try:
            #aggregated_ngrams = {}
            while 1:
                nextsent = sentenceTaggedTokens.next()
                # updates the doc's ngrams
                aggregated_ngrams = self.ngramize(
                    #aggregated_ngrams,
                    minSize = ngramMin,
                    maxSize = ngramMax,
                    tagTokens = nextsent,
                    filters = filters,
                    stemmer = stemmer
                )
        except StopIteration, stopit:
            return
        
    def selectcontent(self, config, doc):
        """
        Adds content fields from application's configuration
        """
        customContent = ""
        for field in config['doc_extraction']:
            try:
                customContent += " . " + doc[ field ]
            except Exception, exc:
                logging.warning("selectcontent : %s"%exc)
        if len(customContent)==0:
            logging.error("document %s content is empty"%doc['_id'])
        return customContent
    
    def sanitize(self, input):
        """
        basic @input text sanitizing
        @return str: text
        """
        # Put blanks before and after '...' (extract ellipsis).
        # Put space between punctuation ;!?:, and following text if space missing.
        # Put space between text and punctuation ;!?:, if space missing.
        punct2find_re.sub(
            punct2find_subst,
            punct1find_re.sub(
                punct1find_subst,
                ellipfind_re.sub(
                    ellipfind_subst,
                    input
                )
            )
        )
        return string.strip(input)

    def tokenize(self, text, tagger):
        """
        Cuts a @text in sentences of tagged tokens
        using nltk Treebank tokenizer
        and a @tagger object
        """
        sentences = nltk.sent_tokenize(text)
        for sent in sentences:
            yield tagger.tag(nltk_treebank_tokenizer.tokenize(sent))

    def ngramize(self, minSize, maxSize, tagTokens, filters, stemmer):
        """
        common ngramizing method
        returns a dict of filtered NGram instances
        using the optional stopwords object to filter by ngram length

        @tagTokens == [[word1 tokens], [word2 tokens], etc]
        """
        # content is the list of words from tagTokens
        content = tagger.TreeBankPosTagger.getContent(tagTokens)
        stemmedcontent = []
        doc_ngrams = []
        for word in content:
             stemmedcontent += [stemmer.stem(word)]
        # tags is the list of tags from tagTokens
        tags = tagger.TreeBankPosTagger.getTag(tagTokens)
        for i in range(len(content)):
            for n in range(minSize, maxSize + 1):
                if len(content) >= i + n:
                    # updates document's ngrams cache
                    ngid = getNodeId(stemmedcontent[i:n+i])
                    label = getNodeLabel(content[i:n+i])
                    ngram = self.storage.ngrams.find_one({'id': ngid})
                    if ngram is not None:
                        if ngid not in doc_ngrams:
                            self.storage.ngrams.update(
                                { 'id': ngid },
                                {
                                    "$inc" : {
                                        'weight': 1
                                    }
                                }
                            )
                        self.storage.ngrams.update(
                            { 'id': ngid },
                            {
                                "$inc" : {
                                    'edges': {
                                        'label' : { label: 1 }
                                    }
                                },
                                'edges': {
                                    'postag' : { label: tags[i:n+i] }
                                }
                            }
                        )
                        upedges = {
                            'label': { label : 1 },
                            'postag': { label : tags[i:n+i] }
                        }
                    else:
                        doc_ngrams += [ngid]
                        # id made from the stemmedcontent and label made from the real tokens
                        ngdict = {
                            'content': content[i:n+i],
                            '_id': ngid,
                            'id': ngid,
                            'label': label,
                            'weight': 1,
                            'edges': {
                                'postag' : { label : tags[i:n+i] },
                                'label': { label : 1 }
                            },
                            'postag' : tags[i:n+i]
                        }
                        ngram = NGram(ngdict)
                        # application defined filtering
                        if filtering.apply_filters(ngram, filters) is True:
                            ngrams[ngid] = ngram
                            logging.debug(ngram['label'])
        return ngrams