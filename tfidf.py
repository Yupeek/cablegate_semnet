import pymongo
from pymongo import Connection
MONGODB_PORT = 27017
import nltk
from nltk.corpus import brown
from nltk.text import TextCollection
mongodb=Connection("localhost", MONGODB_PORT)['cablegate']
browntext = TextCollection(brown.words(categories=['news','government']))
count=0
for ng in mongodb.ngrams.find(timeout=False):
	mongodb.ngrams.update({"_id":ng["_id"]},{"$set":{"tfidf": browntext.tf_idf(ng['label'],brown.words(categories=['news','government'])) }})
	count+=1
	print "updated tfidf for %d topics"%count
