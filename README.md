#Mapping Cablegate thematics using Python, MongoDB and Gephi


Talk proposal : [FOSDEM data dev room](http://datadevroom.couch.it/), Brussels, Feb 5-7 2011, 

##Speakers

 - Julian Bilcke : software developer for the [TINA project](http://tinasoft.eu), contributor for the [Gephi project](http://gephi.org). Follow me at [@flngr](http://twitter.com/flngr).
 - (Elias Showk)[http://github.com/elishowk/] : software engineer at Centre National de la Recherche Scientifique (France). Developer for the [TINA project](http://tinasoft.eu). Its key areas of work are text-mining, building data applications engines with non-relational databases and customized HTTP servers.

##Audience

 - intermediate (to confirm)

##Abstract

We propose to present a complete work-flow of textual data analysis, from acquisition to visual exploration of the network of its thematics. Through the presentation of a (simple software specifically developed for this talk)[http://github.com/elishowk/cablegate-semnet], we will cover a set of productive and widely used softwares and libraries in text analysis, then introduce some features of (Gephi)[http://gephi.org], an open-source network visualization & analysis software, using the data collected and transformed with (cablegate-semnet)[http://github.com/elishowk/cablegate-semnet].

###Data used and methodology

The presentation will focus on Wikileaks' cablegate data, and specially on the full text of all published diplomatic cables yet. The goal is to produce a weighted network.

This networks will contents to parties :

 - cables nodes linked by co-occurrences,
 - word n-grams nodes linked by an adaptation of the Jaccard similarity index.


###Cablegate-semnet python software


This software illustrates common methods of text-mining taking advantage of Python built-in functions as well as some external and famous libraries (NLTK, BeautifulSoup).
It also demonstrate the simplicity and power of [Mongo DB](http://mongodb.org) in tasks of document indexing and information extraction.

 - Reads the local copy of the cablegate site, using built-in OS file handling and some Regular Expressions
 - Parses cables with [NLTK](http://nltk.org)'s HTML cleaning feature, [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)'s HTML parser and Python's regular expressions
 - Inserts cables into Mongo DB, using [Python Mongo DB driver](http://api.mongodb.org/python/1.9%2B/index.html)
 - Automatically extracts relevant word NGram with NLTK
 - Produces a network in a Gephi compatible format ([GEXF](http://gexf.net))
 - optional : Dumps data to various formats

### Gephi demonstration

- How to import a network data file
- Overview of basic visualization features
- How to remove meaningless content using the data table, sorting and filtering
- How to highlight meaningful elements using cluster detection, ranking, coloration
- How to customize the graph appearance, and export the map to PDF and the web
 
##INSTALLATION AND USAGE

`python setup.py develop`
  
 - this will check and install required dependencies

###PREREQUISITES

- Local copy of the cablegate torrent into data/cablegate.wikileaks.org/
- MongoDB (http://www.mongodb.org)
- please fetch manually a stable version of pymongo for your system (the pypi one is broken) : http://api.mongodb.org/python/1.9%2B/index.html
  
#### Gephi Software

- You can try Gephi yourself by downloading it from the [downloads page](http://gephi.org/users/download/).
- For any question try the [Gephi forums](http://forum.gephi.org) or [@Gephi](http://twitter.com/gephi) on Twitter.
- You can follow the 5-min tutorial here: [quick-start tutorial](http://gephi.org/users/quick-start/)

###USAGE

  - start your mongod daemon
  - find command-line help :
  
`python cablegate_semnet.py -h`

  - to export all the data run:
  
`mongoexport -d cables -c cables -o dump/cables.json`


###JSON OUTPUT

`cable = {
  "_id" : "XXX",
  "origin" : "EMBASSY NAME",
  "date_time" : "2000-00-00 00:00",
  "classification" : "TAG",
  "content" : "text",
  "label" : "label",
  "id" : "XXX"
}`