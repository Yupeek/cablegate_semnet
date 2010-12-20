
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")

from cableimporter import CableImporter
from mongodbhandler import CablegateMongo
from datamodel import Cable, getNodeId, getNodeLabel, updateNodesEdges, Document, NGram
from cablegateextractor import CableExtractor

import tinasoft
from tinasoft.pytextminer import PyTextMiner, tagger, filtering, stemmer, stopwords, tokenizer, corpus, whitelist


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-a", "--archive", dest="archive", help="cablegate archive path", metavar="FILE")
    parser.add_option("-o", "--occurrences", dest="minoccs", help="minimum keyphrase occurrence", metavar="int")
    (options, args) = parser.parse_args()