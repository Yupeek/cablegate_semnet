#Mapping Cablegate thematics using Python, MongoDB and Gephi


FOSDEM data dev room
Brussels, Feb 5-7 2011
http://datadevroom.couch.it/

##Speakers

 - Julian Bilcke : (contacts, short bio)
 - Elias Showk : (contacts, short bio)


##Audience

 - intermediate

##Abstract

We propose to present a complete work-flow of textual data analysis, from acquisition to visual exploration of the network of its thematics. Through the presentation of a simple software specifically developed for this talk (http://github.com/elishowk/cablegate-semnet), we would like to provide an overview of productive and widely used softwares and libraries in text analysis, then introduce the basic usage of Gephi, a network analysis software (http://gephi.org).

###Data used and methodology

The presentation will focus on Wikileak’s cablegate data, and specially on the full text of all published diplomatic cables yet. The goal is to produce a weighted network.

This networks will contents to parties :
 - cables nodes linked by co-occurrences,
 - word ngrams nodes linked by an adaptation of the Jaccard similarity index.


###Cablegate-semnet python softwar


This sofware illustrates common methods of text-mining taking advantage of Python built-in functions () as well as some external and famous libraries (NLTK, BeautifulSoup, ).
It also demonstrate the simplicity and power of Mongo DB in tasks of document indexing and information extraction.

 - Reads the local copy of the cablegate site
 - Parses cables with NLTK and BeautifulSoup
 - Inserts cables into Mongo DB
 - Automatic more relevant word NGram with NLTK
 - Produces a network in a Gephi compatible format (GEXF)
 - Dumps data to various formats

##INSTALLATION AND USAGE

$ python setup.py develop
  
 - this will check and install required dependencies

###PREREQUISITES

- Local copy of the cablegate website to copy into data/cablegate.wikileaks.org/
- MongoDB (www.mongodb.org)
- fetch manually a stable version of pymongo for your system : http://api.mongodb.org/python/1.9%2B/index.html
  

###USAGE

  - start your mongod daemon
  - find command-line help :
  
$ python cablegate_semnet.py -h
  - to export all the data run:
$ mongoexport -d cables -c cables -o dump/cables.json


###JSON OUTPUT

cable = {
  "_id" : "XXX",
  "origin" : "EMBASSY NAME",
  "date_time" : "2000-00-00 00:00",
  "classification" : "TAG",
  "content" : "text",
  "label" : "label",
  "id" : "XXX"
}