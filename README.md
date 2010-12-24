#Mapping Wikileaks' Cablegate thematics using Python, MongoDB and Gephi

Talk proposal for [FOSDEM's data dev room](http://datadevroom.couch.it/), Brussels, Feb 5 2011, 

##Speakers

We are two software engineers at Centre National de la Recherche Scientifique (France) working on the [TINA project](http://tinasoft.eu).

 - [Julian Bilcke](http://github.com/jbilcke) : contributor for the [Gephi project](http://gephi.org). Follow me at [@flngr](http://twitter.com/flngr).
 - [Elias Showk](http://github.com/elishowk) : Its key areas of work are text-mining with python, building data applications engines with non-relational databases and customized HTTP servers. Also codes Javascript/JQuery/HTML5 web interfaces and, less recently, Perl/Moose/Catalyst modules. Follow me [@elishowk](http://identi.ca/elishowk)

##Audience

 - intermediate or beginner

##Abstract

We propose to present a complete work-flow of textual data analysis, from acquisition to visual exploration of a complex network. Through the presentation of a [simple software specifically developed for this talk](http://github.com/elishowk/cablegate_semnet), we will cover a set of productive and widely used softwares and libraries in text analysis, then introduce some features of [Gephi](http://gephi.org), an open-source network visualization & analysis software, using the data collected and transformed with [cablegate-semnet](http://github.com/elishowk/cablegate_semnet).

###Data used and methodology

The presentation will focus on Wikileaks' cablegate data, and specially on the full text of all published diplomatic cables yet. The goal is to produce a weighted network. This network will contain two categories of nodes :

 - thematics nodes linked by co-occurrences, automatically extracted from full-text
 - leaked cables nodes linked by a custom similarity index (adaptation of [Jaccard similarity index](http://en.wikipedia.org/wiki/Jaccard_index)).
 
Both categories will be linked by occurrences.

###1st Part : Cablegate-semnet python software internals demonstration

 - speaker : Elias

This software illustrates common methods of text-mining taking advantage of Python built-in functions as well as some external and famous libraries ([NLTK](http://nltk.org), [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)).
It also demonstrate the simplicity and power of [Mongo DB](http://mongodb.org) in tasks like document indexing and information extraction.

The talk will focus on the following topics :

 - Parses cables with NLTK's HTML cleaner, BeautifulSoup's HTML parser and [Python's regular expressions](http://docs.python.org/library/re.html)
 - Inserts cables into Mongo DB using its internal JSON format, and presenting [the Python driver for Mongo DB](http://api.mongodb.org/python/1.9%2B/index.html)
 - Extracts relevant keyphrases with NLTK : part-of-speech tagging, stemming, keyphrases selection based on a grammar, Mongo DB atomic modifiers.
 - Pre-processes the network with [Mongo DB's map/reduce capabilities](http://www.mongodb.org/display/DOCS/MapReduce) to get edges' weight between nodes.
 - Exports the network in a Gephi compatible format ([GEXF](http://gexf.net)) using [Tenjin template engine](http://www.kuwata-lab.com/tenjin/)


###2nd part : Gephi demonstration

 - speaker : Julian

Cablegate-semnet has a quite naive automatic selection of text thematics and produces a network of thousands of nodes but containing some noise. On the other hand, the presence of two types of nodes implies three types of edges so that we can expect a [dense graph](http://en.wikipedia.org/wiki/Dense_graph). As a conclusion, we produce a weighted network quite rich in information, so the aim of this second part is to demonstrate Gephi's features in network post-processing, with a focus on :

- How to import a network data file
- Overview of basic visualization features
- How to remove meaningless content using the data table, sorting and filtering
- How to highlight meaningful elements using cluster detection, ranking, coloration
- How to customize the graph appearance, and export the map to PDF and the web
