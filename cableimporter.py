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
from datamodel import initEdges
from mongodbhandler import CablegateDatabase
from cablemap.core import cables_from_directory
from cablemap.core.utils import titlefy


class CableImporter(object):
    """
    Reads and parses all available cables and updates the mongodb
    """
    counts = {
      'files_not_processed':0
    }

    def __init__(self, config, data_directory, overwrite=False, maxcables=None):
        self.data_directory = join(data_directory, "cable")
        self.mongodb = CablegateDatabase(config['general']['mongodb'])["cablegate"]
        if overwrite is True and "cables" in self.mongodb.collection_names():
            self.mongodb.drop_collection("cables")
        self.walk_archive(overwrite, maxcables)

    def walk_archive(self, overwrite, maxcables):
        """
        Walks the archive directory
        """
        self.cable_list=[]
        try:
            for cable in cables_from_directory(self.data_directory):
                self.process_cable(cable, overwrite)
                if maxcables is not None and len(self.cable_list) >= maxcables:
                    break
        except OSError, oserr:
            logging.error("%s"%oserr)

    def process_cable(self, cb, overwrite):
        """
        Cable Content extractor
        """
        cable_id = cb.reference_id
        cable = self.mongodb.cables.find_one({'_id': cable_id})
        if not overwrite and cable is not None:
            logging.info('CABLE ALREADY EXISTS : SKIPPING')
            self.cable_list.append(cable_id)
            logging.info("cables processed = %d, %s" % (len(self.cable_list), cb.reference_id))
            return
        ## updates metas without erasing edges
        if cable is None:
            cable = initEdges({})
        ## overwrite metas informations without erasing edges
        cable.update({
            # auto index
            '_id' : "%s" % cable_id,
            'label' : titlefy(cb.subject),
            'start' : datetime.strptime(cb.created, "%Y-%m-%d %H:%M"),
            'classification' : cb.classification,
            'embassy' : cb.origin,
            'content' : cb.content,
            'category': "Document"
        })
        self.mongodb.cables.save(cable)
        self.cable_list.append(cable_id)
        logging.info(u"cables processed = %d, %s" % (len(self.cable_list), cb.reference_id))
