import logging
import os
import re
import sys
import xml
import csv
import subprocess

from BeautifulSoup import BeautifulSoup

LF = '&#x000A;'
PRECEDENCE = {'ZZ': 'FLASH',
              'OO': 'IMMEDIATE',
              'PP': 'PRIORITY',
              'RR': 'ROUTINE'}

logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

def get_soup_text(bs):
  return ''.join(bs.findAll(text=True)).strip()

class Cable(object):
  
  raw = ""
  id = None
  
  def __init__(self, raw, extract_content=True):
    #self.raw = raw
    logging.info('Cable()')
    if extract_content is True:
      self.extract_content(raw)
  
  def parse_wikileaks_header(self, bs):
    top = bs.find("table", { "class" : "cable" }).findAll('td')
    self.id = get_soup_text(top[0])
    self.datetime = get_soup_text(top[1])
    self.released = get_soup_text(top[2])
    self.classification = get_soup_text(top[3])
    self.origin = get_soup_text(top[4])

  def parse_cable_header(self, bs):
    header = bs.findAll('pre')[0]
    self.raw_header_display = get_soup_text(header)
    hdlst = self.raw_header_display.split(LF, 6)
    self.tx_id = hdlst[0]
    self.precedence = PRECEDENCE[hdlst[1][0:2]]
    self.destination_ri = hdlst[1][3:].split(' ')
    foo, self.origin_ri, self.origin_serno, self.tx_time = hdlst[2].split(' ')
    fl4 = hdlst[3].split(' ')
    self.opsig = [fl4[0]]
    self.classgrp = fl4[1]
    if len(fl4) > 2:
      self.opsig.extend(fl4[2:])
    self.datetimegrp = hdlst[4]
    self.origin_plad = hdlst[5][3:]
    # just a hack for now...
    self.destination_plad = hdlst[6]

  def parse_cable_body(self, bs):
    self.body = get_soup_text(bs.findAll('pre')[1])

  def extract_content(self, raw):
    logging.info('Cable.extract_content')
    soup = BeautifulSoup(raw)
    self.parse_wikileaks_header(soup)
    self.parse_cable_header(soup)
    self.parse_cable_body(soup)
    
class Processor():
  
  data_directory = 'data/cablegate/cablegate.wikileaks.org/cable'
  
  country_dictionary_path = 'data/countries.csv'
  countries = []
  #country_frequency = nltk.probability.FreqDist()
  
  file_regex = re.compile("\.html$")
  
  counts = {
    'files_to_process':0,
    'files_processed':0,
    'files_not_processed':0
  }
  
  def __init__(self):
    logging.info('Processor()')
    self.load_countries()
#    self.process()
  
  # def process(self):
  #   logging.info('Processor.process')
  #   self.read_files()
  
  def load_countries(self):
    logging.info('Processor.load_countries')
    try:
      file = open(self.country_dictionary_path,'r')
    except OSError:
      logging.warning('Processor.CANNOT OPEN FILE '+path)
      return
    countries = csv.reader(file, delimiter=',')
    for row in countries:
      self.countries.append(row[1].lower())
    
  def read_files(self):
    logging.info('Processor.read_files')
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
  
  def print_counts(self):
    logging.info('Processor.print_counts')
    logging.info(str(self.counts['files_to_process'])+" | "+\
      str(self.counts['files_processed'])+" | "+\
      str(self.counts['files_not_processed']))
  
  def dump_json(self):
    logging.info('Processor.dump_json')
 