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

import filtering

from datamodel import getNodeId, getNodeLabel, updateNodeEdges, overwriteEdge, addEdge, addUniqueEdge

import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

nltk_treebank_tokenizer = nltk.TreebankWordTokenizer()

# We consider following rules to apply before tokenizing
# A regexp to put spaces if missing after/before alone marks.
punct1find_re = re.compile(ur"(["+string.punctuation+"])([^\s])", re.IGNORECASE|re.VERBOSE)
# A regexp to put spaces if missing before alone marks.
punct2find_re = re.compile(ur"([^\s])([["+string.punctuation+"])", re.IGNORECASE|re.VERBOSE)
punct_subst = ur"\1 \2"

# A regexp to remove multiple minus signs in cables
multisign_re = re.compile(ur"-+", re.IGNORECASE|re.VERBOSE)
multisign_subst = ur" \. "

# A regexp to match non-alphanumeric
#nonalphanum_re = re.compile(ur"[^ \w\s]", re.IGNORECASE|re.VERBOSE)
#nonalphanum_subst = ur""

# A regexp to match html entities like '&#x000A;'
htmlentities_re = re.compile(ur"\&\#x[\d]{1,3}[A-Za-z]{1}\;", re.IGNORECASE|re.VERBOSE)
htmlentities_subst = ur" "

class NGramizer(object):
    """
    A tokenizer that divides a text into sentences
    then cleans the punctuation
    before tokenizing using nltk.TreebankWordTokenizer()
    """
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config

    def extract(self, documentObj, filters, tagger, stemmer):
        """
        sanitizes content and label texts
        tokenizes it
        POS tags the tokens
        constructs the resulting NGram objects
        """
        ngramMin = self.config['ngramMin']
        ngramMax = self.config['ngramMax']

        sentenceTaggedTokens = self.tokenize(
            self.sanitize(
                self.selectcontent(documentObj)
            ),
            tagger
        )
        try:
            aggregated_ngrams = []
            while 1:
                nextsent = sentenceTaggedTokens.next()
                # updates the doc's ngrams
                aggregated_ngrams = self.ngramize(
                    documentObj,
                    aggregated_ngrams,
                    minSize = ngramMin,
                    maxSize = ngramMax,
                    tagTokens = nextsent,
                    filters = filters,
                    stemmer = stemmer
                )
        except StopIteration, stopit:
            logging.info("finished extraction of %d ngrams on cable %s"%(len(aggregated_ngrams),documentObj['_id']))
            return aggregated_ngrams

    def selectcontent(self, doc):
        """
        Adds content fields from application's configuration
        """
        customContent = ""
        for field in self.config['doc_extraction']:
            try:
                customContent += " . " + doc[ field ]
            except Exception, exc:
                logging.warning("selectcontent : %s"%exc)
        if len(customContent)==0:
            logging.error("document %s content is empty"%doc['_id'])
        return customContent

    def sanitize(self, input):
        """
        @input content text to sanitize
        @return str: text
        """
        # TODO ?
        # Put blanks before and after '...' (extract ellipsis).
        # Put space between punctuation ;!?:, and following text if space missing.
        # Put space between text and punctuation ;!?:, if space missing.
        output = punct2find_re.sub(
            punct_subst,
            punct1find_re.sub(
                punct_subst,
                multisign_re.sub(
                    multisign_subst,
                    htmlentities_re.sub(
                        htmlentities_subst,
                        input
                    )
                )
            )
        )
        return output.strip()

    def tokenize(self, text, tagger):
        """
        Cuts a @text in sentences of tagged tokens
        using nltk Treebank tokenizer
        and a @tagger object
        """
        sentences = nltk.sent_tokenize(text)
        for sent in sentences:
            yield tagger.tag(
                nltk_treebank_tokenizer.tokenize(
                    sent
                )
            )
    
    def getContent( self, sentence ):
        """return words from a tagged list like [["the","DET"],["python","NN"]]"""
        return [tagged[0] for tagged in sentence]

    def getTag( self, sentence ):
        """return TAGS from a tagged list like [["the","DET"],["python","NN"]]"""
        return [tagged[1] for tagged in sentence]

    def ngramize(self, document, doc_ngrams, minSize, maxSize, tagTokens, filters, stemmer):
        """
        common ngramizing method
        returns a dict of filtered NGram instances
        @tagTokens == [[word1 tokens], [word2 tokens], etc]
        """
        # content is the list of words from tagTokens
        content = self.getContent(tagTokens)
        stemmedcontent = []
        for word in content:
             stemmedcontent += [stemmer.stem(word)]
        # tags is the list of tags from tagTokens
        tags = self.getTag(tagTokens)
        for i in range(len(content)):
            for n in range(minSize, maxSize + 1):
                if len(content) >= i+n:
                    # updates document's ngrams cache
                    ngid = getNodeId(stemmedcontent[i:n+i])
                    label = getNodeLabel(content[i:n+i])
                    ngram = self.storage.ngrams.find_one({'_id': ngid})
                    if ngram is not None:
                        # general edges updates
                        ngram = overwriteEdge( ngram, 'postag', label, tags[i:n+i])
                        ngram = addEdge( ngram, 'Document', document['_id'], 1)
                        ngram = addEdge( ngram, 'label', label, 1)
                        self.storage.ngrams.save(ngram)
                        document = addEdge( document, 'NGram', ngid, 1 )
                        self.storage.cables.save(document)
                    else:
                        # id made from the stemmedcontent and label made from the real tokens
                        try:
                            ngram = {
                                '_id': ngid,
                                'id': ngid,
                                'label': label,
                                'content': content[i:n+i],
                                'edges': {
                                    'postag' : { label : tags[i:n+i] },
                                    'label': { label : 1 },
                                    'Document': { document['_id'] : 1 },
                                    'NGram': {}
                                },
                                'postag' : tags[i:n+i]
                            }
                            # application defined filtering
                            if filtering.apply_filters(ngram, filters) is True:
                                doc_ngrams += [ngid]
                                self.storage.ngrams.save(ngram)
                                document = addEdge( document, 'NGram', ngid, 1 )
                                self.storage.cables.save(document)
                        except Exception, exc:
                            logging.error("error inserting new ngram %s : %s"%(label, exc))

        return doc_ngrams
