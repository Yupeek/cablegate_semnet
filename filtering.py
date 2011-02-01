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

__author__="elishowk"

import re
import logging
_logger = logging.getLogger('TinaAppLogger')

def apply_filters(ngram, filters=None):
    """
    use it like this :
    if filtering.apply_filters(ngram_class_instance, filterslist) is False:
        block the ngram
    """
    if filters is not None:
        for filt in filters:
            if filt.test(ngram) is False:
                return False
    return True


class Content():
    """
    Rule-based NGram content filtering
    applies on a generator of (ngram_objects)
    """
    # TODO move rules into app config, and add language support
    rules = {
        'any':[''],
        'begin':[],
        'end':[],
        'both':['by','in','of','a','have','is','are','or','and',],
    }
    lang='en'

    def __init__(self, config=None):
        """default rules based on english stopwords"""
        if config is not None:
            if 'rules' in config:
                self.rules = config['rules']
            if 'lang' in config:
                self.lang = config['lang']

    def get_content(self, ng):
        return ng['content']

    def _any(self, ng):
        contents = self.get_content(ng)
        for content in contents:
            if content in self.rules['any']:
                return False
        return True

    def _both(self, ng):
        contents = self.get_content(ng)
        test = True
        if contents is not None:
            if contents[0] in self.rules['both'] or contents[-1] in self.rules['both']:
                test = False
        return test

    def _begin(self, ng):
        contents = self.get_content(ng)
        test = True
        if contents is not None:
            if contents[0] in self.rules['begin']:
                test = False
        return test

    def _end(self, ng):
        contents = self.get_content(ng)
        test = True
        if contents is not None:
            if contents[-1] in self.rules['end']:
                test = False
        return test


    def test(self, ng):
        """returns True if ALL the tests passed"""
        return self._any(ng) and self._both(ng) and self._begin(ng) and self._end(ng)

class WordSizeFilter(Content):
    """
    Word length filtering
    """
    def test(self, ng):
        """returns True if ALL the tests passed"""
        content = self.get_content(ng)
        test = True
        for word in content:
            if len(word) < self.rules['minWordSize']:
                test = False
        return test

    def get_content(self, ng):
        """selects NGram's postag"""
        return ng['content']


class PosTagValid(Content):
    """
    Regexp-based POS tag filtering validation
    """

    def get_content(self, ng):
        """selects NGram's postag"""
        return ng['postag']

    def test(self, ng):
        """returns True if ALL the tests passed"""
        content = self.get_content(ng)
        pattern = ",".join(content)
        pattern += ","
        if self.rules.match(pattern) is None:
            return False
        else:
            return True
