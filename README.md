#Mapping Wikileaks' Cablegate thematics using Python, MongoDB, Neo4j and Gephi

Talk at [FOSDEM 2011's data dev room](http://datadevroom.couch.it/), Brussels, Feb 5 2011,

 - [Talk slides and video are here](http://elishowk.github.com/cablegate_semnet)
 - [Some data sets are here](http://tina.iscpif.fr/htdocs/fosdem2011/dataset)

##Speakers

We are two software engineers at Centre National de la Recherche Scientifique (France) working on the [TINA project](http://tinasoft.eu).

 - [Julian Bilcke](http://github.com/jbilcke) : contributor for the [Gephi project](http://gephi.org). Follow me at [@flngr](http://twitter.com/flngr).
 - [Elias Showk](http://github.com/elishowk) : text-miner with python, data applications architect, using non-relational databases and customized HTTP servers. Also codes Javascript/JQuery/HTML5 web interfaces and, less recently, Perl/Moose/Catalyst modules. Follow at [@elishowk](http://identi.ca/elishowk) or at [@elishowk](http://twitter.com/elishowk)

##Abstract

We propose to present a complete work-flow of textual data analysis, from acquisition to visual exploration of a complex network. Through the presentation of a [simple software specifically developed for this talk](https://github.com/elishowk/cablegate_semnet), we will cover a set of productive and widely used open-source softwares and libraries, then introduce some features of [Gephi](http://gephi.org), a free network visualization & analysis software, using the data collected and transformed with [the cablegate semnet app](http://github.com/elishowk/cablegate_semnet).

###Data and methodology

The presentation will focus on Wikileaks' cablegate data, and specially on the full text of all published diplomatic cables yet. The goal is to produce a weighted network. This network will contain two categories of nodes :

 - thematics nodes linked by co-occurrences, automatically extracted from full-text
 - cables and topics are linked by occurrences.

###About the project

It's a quickly hacked software we worked on during our free time, in order to learn about some recent technologies, and also because Wikileaks' Cablegate is an interesting topic, with a lot of full-text data to analyze.

Since the FOSDEM is an engineering/hacking event, our talk was focused on the process, on showing how we took advantage of powerful tools to dig into textual data and produce an overview of this medium-sized corpus. Topic maps are fascinating and useful, and we wanted to share our knowledge about it. One can produce them from any available text data on the web (Wikileaks, open data, web crawls, etc). Our goals are summarized in [this slide](http://elishowk.github.com/cablegate_semnet#slide2)

We are interested in a deeper analysis of the network, but we lacked some time to elaborate on the maps, so we had to rush to finalize a first version of the maps, in order to be ready for the FOSDEM.

However we are still trying to improve it, and future version of the network should be better (cleaner topics, less "meaningless" words) and more useful for exploration.

###About the data

Since we worked on the publicly released cables, we didn't expect any more that what the medias (Wikileaks, Guardian..) choosed, namely* *0.1% of the
cables.

So, we didn't find any unexpected secret, and even if we had, it would have been already covered by the media. This is because our maps mare mostly a tool for exploration, to help people dig into a large datasets of intricated cables, and topics.

In a sense, it help seeing the top topics (more generals), and dig into the hierarchy, level after level. You can see potentially interesting cable stories at a glance, just by looking at what seems to be clusters (sub-networks) in the map, and zoom in for details. We believe this can be used as a complement to other cablegate tools we have seen so far, like search-engines, and categorial or geographic representations. But still, there is a publication biais : we only see what have been already released and censored.

###Articles

  - [FOSDEM: Mapping WikiLeaks using open-source tools, by Koen Vervloesem](https://lwn.net/Articles/427054/)

