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

import os
from os.path import join
import re
import nltk
from BeautifulSoup import BeautifulSoup
from datamodel import Cable

class CableImporter(object):
  
    """
    Reads and parses all available cables and updates the mongodb
    usage : mirror = CableGateMirror(wikileaksdb, 'data/cablegate.wikileaks.org')
    """
    
    file_regex = re.compile("\.html$")
    
    counts = {
      'files_to_process':0,
      'files_processed':0,
      'files_not_processed':0
    }
  
    def __init__(self, db, data_directory):
        self.data_directory = join(data_directory, "cable")
        self.db = db
        self.read_files()
    
    def read_files(self):
        logging.info('Processor.read_files')
        try:
            for root, dirs, files in os.walk(self.data_directory):
                for name in files:
                    if self.file_regex.search(name) is not None:
                        path = root+"/"+name
                        self.counts['files_to_process'] = self.counts['files_to_process'] + 1
                        self.read_file(path)
        except OSError, oserr:
            logging.error("%s"%oserr)
  
    def read_file(self,path):
        logging.info('Processor.read_file')
        try:
            file = open(path)
        except OSError:
            logging.warning('Processor.read_file : CANNOT OPEN FILE %s, skipping...s'%path)
            self.counts['files_not_processed'] = self.counts['files_not_processed'] + 1
            return
        self.extract_content(file.read())
    
    def extract_content(self,raw):
        logging.info('Processor.extract_content')
        
        soup = BeautifulSoup(raw)
        
        cable_table = soup.find("table", { "class" : "cable" })
        
        cable_id = cable_table.findAll('tr')[1].findAll('td')[0].contents[1].contents[0]
        
        if self.db.cables.find_one({'_id':cable_id}):
            logging.info('Processor.extract_content["CABLE ALREADY EXISTS : OVERWRITTING"]')
            self.db.cables.remove({'_id':cable_id})
          
        kwarguments = {
            '_id' : cable_id,
            'id' : cable_id,
            'label' : cable_id,
            'date_time' : cable_table.findAll('tr')[1].findAll('td')[1].contents[1].contents[0],
            'classification' : cable_table.findAll('tr')[1].findAll('td')[3].contents[1].contents[0],
            'origin' : cable_table.findAll('tr')[1].findAll('td')[4].contents[1].contents[0],
            'content' : nltk.clean_html(str(soup.findAll(['pre'])[1]))
        }
            
        cable = Cable()
        cable.update( kwarguments )
        cable._parseLabel()
        
        print cable
        
        self.db.cables.insert(cable.__dict__)
        
        self.counts['files_processed'] = self.counts['files_processed'] + 1
        self.print_counts()
        
        if (self.counts['files_processed'] + self.counts['files_not_processed'])\
          == self.counts['files_to_process']:
          self.dump_json()
    
    def print_counts(self):
        logging.info(str(self.counts['files_to_process'])+" | "+\
            str(self.counts['files_processed'])+" | "+\
            str(self.counts['files_not_processed']))
    
    def dump_json(self):
        logging.info('Processor.dump_json')