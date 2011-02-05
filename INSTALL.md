##INSTALLATION AND USAGE

- you can run it directly from the code directory
- this will check and install required dependencies : `python setup.py develop`

###PREREQUISITES

- Local copy of the cablegate torrent into data/cablegate.wikileaks.org/
- MongoDB (http://www.mongodb.org)
- Neo4j (http://neo4j.org) and neo4j.py with python-jpype
- please fetch manually a stable version of pymongo for your system (the pypi one is broken) : http://api.mongodb.org/python/1.9%2B/index.html

#### Gephi Software

- You can try Gephi yourself by downloading it from the [downloads page](http://gephi.org/users/download/).
- For any question try the [Gephi forums](http://forum.gephi.org) or [@Gephi](http://twitter.com/gephi) on Twitter.
- You can follow the 5-min tutorial here: [quick-start tutorial](http://gephi.org/users/quick-start/)

###USAGE

  - start your mongod daemon
  - find command-line help :

`python execute.py -e import|extract|network ...`


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
