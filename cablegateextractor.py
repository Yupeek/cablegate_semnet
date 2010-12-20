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

class CableExtractor(object):
  """
  Reads all database entries to produce a network
  usage :
  extractor = Exporter(minoccs=2)
  """
  def __init__(self,config, minoccs=1):
    self.config = config
    white = self.extract_cables(minoccs)
    
  def extract_cables(self,minoccs):
    filters = self._get_extraction_filters()
    cursor = db.cables.find()
    cable_gen = self.cable_generator()
    newwl = whitelist.Whitelist("cablegate", "cablegate")
    # instanciate the tagger, takes times on learning
    postagger = tagger.TreeBankPosTagger(
      training_corpus_size = 10000,
      trained_pickle = "tagger.pickle"
    )
    try:
      while 1:
        # gets the next document
        document, year = cable_gen.next()
        document['edges']['Corpus'][year]=1
        # extract and filter ngrams
        docngrams = tokenizer.TreeBankWordTokenizer.extract(
            document,
            self.config,
            filters,
            postagger,
            stemmer.Nltk()
        )
        ### updates newwl to prepare export
        if  year not in newwl['corpus']:
            newwl['corpus'][year] = corpus.Corpus(year)
        newwl['corpus'][year].addEdge('Document', document['id'], 1)

        for ng in docngrams.itervalues():
          newwl.addContent( ng, year, document['id'] )
          newwl.addEdge("NGram", ng['id'], 1)
        newwl.storage.flushNGramQueue()
            
    except StopIteration:
      whitelist_exporter = Writer("whitelist://cable_extraction.csv")
      (filepath, newwl) = whitelist_exporter.write_whitelist(newwl, minoccs)
      return newwl
    
  def cable_generator(self):
    """
    generator of cables from mongodb
    """
    self.total_cables = db.cables.count()
    cursor = db.cables.find()
    while self.total_cables > 0:
      logging.info("remaining %d cables to process"%self.total_cables)
      cable = cursor.next() 
      yield (cable, cable['date_time'][:4])
      self.total_cables -= 1
    self.total_cables = db.cables.count()
    return

  def _get_extraction_filters(self):
    """
    returns extraction filters
    """
    filters = [filtering.PosTagValid(
      config = {
        'rules': re.compile(self.config['datasets']['postag_valid'])
      }
    )]
    filters += [stopwords.StopWords(
      "file://%s"%join(
        self.config['general']['basedirectory'],
        self.config['general']['shared'],
        self.config['general']['stopwords']
      )
    )]
    return filters  

  def index_cables(self):
    return