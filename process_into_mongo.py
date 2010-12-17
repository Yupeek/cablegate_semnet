import logging
import os
from os.path import join
import re
import yaml
import nltk
import pymongo
from BeautifulSoup import BeautifulSoup

import tinasoft
from tinasoft.pytextminer import PyTextMiner, tagger, filtering, stemmer, stopwords, tokenizer, corpus, whitelist

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

mongo_conn = pymongo.Connection('localhost', 27017)
db = mongo_conn['wikileaks']

class Cable(PyTextMiner):
  raw = ""
 
  def __init__(self,raw):
    self.raw = raw
    PyTextMiner.__init__(self, ["empty"])
  
  def get(self):
    del self.raw
    return self.__dict__
    
class CableGateMirror():
  
  #mirror_directory = 'data/cablegate/'
  
  def __init__(self):
    logging.info('CableGateMirror()')
    self.update()
    
  def update(self):
    logging.info('CableGateMirror.update')
    Processor()
    

class Processor():
  
  data_directory = 'data/cablegate.wikileaks.org/cable'  
  file_regex = re.compile("\.html$")
  
  counts = {
    'files_to_process':0,
    'files_processed':0,
    'files_not_processed':0
  }
  
  def __init__(self):
    self.read_files()
    
  def read_files(self):
    try:
      for root, dirs, files in os.walk(self.data_directory):
        for name in files:
          if self.file_regex.search(name) is not None:
            path = root+"/"+name
            self.counts['files_to_process'] = self.counts['files_to_process'] + 1
            self.read_file(path)
    except OSError:
      logging.info(str(OSError))
  
  def read_file(self,path):
    logging.info('Processor.read_file')
    try:
      file = open(path)
    except OSError:
      logging.warning('Processor.CANNOT OPEN FILE '+path)
      self.counts['files_not_processed'] = self.counts['files_not_processed'] + 1
      return
    self.extract_content(file.read())
    
  def extract_content(self,raw):
    logging.info('Processor.extract_content')
    
    soup = BeautifulSoup(raw)
    
    cable_table = soup.find("table", { "class" : "cable" })
    
    cable_id = cable_table.findAll('tr')[1].findAll('td')[0]\
      .contents[1].contents[0]
    
    if db.cables.find_one({'_id':cable_id}):
      logging.info('Processor.extract_content["CABLE ALREADY EXISTS : OVERWRITTING"]')
      db.cables.remove({'_id':cable_id})
      
    cable = Cable(raw)
    cable['_id'] = cable_id
    cable['id'] = cable_id
    cable['label'] = cable_id
    cable['date_time'] = cable_table.findAll('tr')[1].findAll('td')[1]\
      .contents[1].contents[0]
    cable['classification'] = cable_table.findAll('tr')[1].findAll('td')[3]\
      .contents[1].contents[0]
    cable['origin'] = cable_table.findAll('tr')[1].findAll('td')[4]\
      .contents[1].contents[0]
    #cable['header'] = nltk.clean_html(str(soup.findAll(['pre'])[0]))
    cable['content'] = nltk.clean_html(str(soup.findAll(['pre'])[1]))
      # here extract title between to expressions
    #SUBJECT: xxx &#x000A;&#x000A;
    res=re.match(r"SUBJECT:(.+)\&\#x000A\;\&\#x000A;", cable['content'])
    cable['label']
    db.cables.insert(cable.get())
    
    self.counts['files_processed'] = self.counts['files_processed'] + 1
    
    self.print_counts()
    
    if (self.counts['files_processed'] + self.counts['files_not_processed'])\
      == self.counts['files_to_process']:
      self.dump_json()
  
  def print_counts(self):
    logging.info('Processor.print_counts')
    logging.info(str(self.counts['files_to_process'])+" | "+\
      str(self.counts['files_processed'])+" | "+\
      str(self.counts['files_not_processed']))
  
  def dump_json(self):
    logging.info('Processor.dump_json')
    
#CableGateMirror()
    
class Exporter(object):
  """
  Reads all database entries to produce a network
  """
  def __init__(self,minoccs=1):
    self.config = yaml.safe_load(file("config.yaml",'rU'))
    print self.config
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
  
Exporter(1)