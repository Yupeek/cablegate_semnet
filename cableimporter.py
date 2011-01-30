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
from datetime import datetime
import re
import nltk
from BeautifulSoup import BeautifulSoup, SoupStrainer
from datamodel import initEdges
from neo4jrestclient.client import GraphDatabase
from cablenetwork import add_node, set_node_attr
from mongodbhandler import CablegateDatabase


class CableImporter(object):

    """
    Reads and parses all available cables and updates the mongodb
    usage : mirror = CableGateMirror(wikileaksdb, 'data/cablegate.wikileaks.org')
    """

    file_regex = re.compile("\.html$")
    title_regex = re.compile("Viewing cable [0-9]+[A-Z]+[0-9]+,",re.U)

    counts = {
      'files_not_processed':0
    }

    def __init__(self, config, data_directory, overwrite=False):
        self.data_directory = join(data_directory, "cable")
        self.mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
        self.graphdb = GraphDatabase(config['general']['neo4j'])
        # soupstrainers avoiding too much html parsing AND memory usage issues !
        self.cablemetasoup = SoupStrainer("div", attrs={ "class" : 'pane big' })
        self.contentsoup = SoupStrainer("pre")
        if overwrite is True and "cables" in self.mongodb.collection_names():
            self.mongodb.cables.remove()
        self.walk_archive(overwrite)


    def walk_archive(self, overwrite):
        """
        Walks the archive directory
        """
        self.cable_list=[]
        try:
            for root, dirs, files in os.walk(self.data_directory):
                for name in files:
                    if self.file_regex.search(name) is None: continue
                    path = join( root, name )
                    self.read_file(path,overwrite)
        except OSError, oserr:
            logging.error("%s"%oserr)

    def read_file(self, path, overwrite):
        """
        Reads the cable file
        """
        logging.info('CableImporter.read_file')
        try:
            file = open(path)
        except OSError:
            logging.warning('Processor.read_file : CANNOT OPEN FILE %s, skipping...s'%path)
            self.counts['files_not_processed'] += 1
            return
        self.extract_content(file.read(), overwrite)

    def extract_content(self, raw, overwrite):
        """
        Cable Content extractor
        """
        try:
            cablemetasoup = BeautifulSoup(raw, parseOnlyThese = self.cablemetasoup)
            # extract_title
            title = self.title_regex.sub( "", cablemetasoup.find("h3").contents[0])
            title = title.strip()
            title = title.title()

            cable_table = cablemetasoup.find("table")
            cable_id = cable_table.findAll('tr')[1].findAll('td')[0].contents[1].contents[0]
            cable = self.mongodb.cables.find_one({'_id': cable_id})

            if overwrite is False and cable is not None:
                logging.info('CABLE ALREADY EXISTS : SKIPPING')
                self.cable_list += [cable_id]
                logging.info("cables processed = %d"%len(self.cable_id))
                return

            ## updates metas without erasing edges
            if cable is None:
                cable = {}
                cable = initEdges(cable)

            contentsoup = BeautifulSoup(raw, parseOnlyThese = self.contentsoup)
            cablecontent = unicode( nltk.clean_html( str( contentsoup.findAll("pre")[1] ) ), encoding="utf_8", errors="replace" )
            del raw
            date_time = datetime.strptime(cable_table.findAll('tr')[1].findAll('td')[1].contents[1].contents[0], "%Y-%m-%d %H:%M")
            cablenode = add_node(self.graphdb, cable)
            ## overwrite metas informations without erasing edges
            cable.update({
                # auto index
                '_id' : cablenode.id,
                'id' : cable_id,
                'label' : title,
                'start' : date_time,
                'classification' : cable_table.findAll('tr')[1].findAll('td')[3].contents[1].contents[0],
                'origin' : cable_table.findAll('tr')[1].findAll('td')[4].contents[1].contents[0],
                'content' : cablecontent,
                'category': "Document"
            })
            set_node_attr(cable, cablenode)
            # insert or auto overwrites existing cable (indexed by '_id')
            self.mongodb.cables.save(cable)
            self.cable_list += [cable_id]
            logging.info("cables processed = %d"%len(self.cable_list))
        except Exception, exc:
            logging.warning("error importing cable : %s"%exc)
            self.counts['files_not_processed'] += 1
            logging.info("error importing a cable, total NOT processed = %d"%self.counts['files_not_processed'])
