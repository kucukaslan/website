---
title: "MongoDB Migration"
date: 2025-03-15T00:00:00+03:00
tags: ['personal', 'en']
draft: true
---
Since the dawn of (hu)mankind, authors wasted countless hours on writing first a few words of the things they intended to share. Forgive me for avoiding the struggle.

I want to take notes on of a few alternative path to migrate a mongodb database from one server to another. The database may be residing on [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-database) or be a self-managed deployment, it may be a standalone instance or a replica set or a sharded cluster. Some of the methods will work for some and some will not.

## Creating the Source Database
I am not your ordinary 10x engineer, and this is just a blog so I will start by simply orchestrating my multicloud K8s cluster using terraform which somehow also integrates to MongoDB Atlas. You may talk to [grok](https://x.com/i/grok/share/RajuEeC4zcsP2rsdNYWoCwMFh) for the details,  
... but it is time to do business! So let's open the [MongoDB Atlas](https://cloud.mongodb.com) and use the clicky-gui interface to create a new cluster. It is also trivial to (up/down?)load the sample data from the [Atlas Sample Data](https://www.mongodb.com/developer/products/atlas/atlas-sample-datasets/).  
You can do most of it without touching the keyboard! Personally, I love working without keyboard while sitting next to my colleague who *[uses](https://camo.githubusercontent.com/b531f093ee846ede8ac35b76366245a52984dac05ca30e304acd086182eb3736/68747470733a2f2f76696d776179732e6f72672f323031382f726f6d61696e6c2d646f6e742d7573652d76696d2f7572696e616c2d6574697175657474652e6a7067) [vim](https://xkcd.com/378/) [btw](https://xkcd.com/1823/)*. Seeing the spark in his eyes is priceless.

## How?
If you are willing to tolerate some downtime or can you afford to lose some data, you can use good old export and import methods. If you want to minimize or possibly eliminate the downtime, you can use the live migration tools provided by MongoDB, afaiu mongosync may also allow live migration.

### Export and Import (Dump and Restore)
<!-- TODO Fix the link-->
![Export Import](../static/img/importer-exporter.gif)
It is quite easy to export and import data using the [MongoDB Compass](https://www.mongodb.com/products/compass). You can also use [mongoimport](https://www.mongodb.com/docs/database-tools/mongoimport/) and [mongoexport](https://www.mongodb.com/docs/database-tools/mongoexport/) command line tools to export the ***data***.

The catch is that you can only export the data, not the indexes, users, or other metadata.

Fortunately, there are alternatives: [mongodump](https://www.mongodb.com/docs/database-tools/mongodump/) and [mongorestore](https://www.mongodb.com/docs/database-tools/mongorestore/). _mongodump_ dumps
> * Collection documents, metadata, and options.
> * Index definitions.
> * Writes that occur during the export, if run with the mongodump --oplog option.[^dump].

[^dump]: [MongoDB Documentation](https://www.mongodb.com/docs/database-tools/mongodump/#:~:text=mongodump%20dumps%3A,%2D%2Doplog%20option.)

So, we can recover indices and metadata using _mongorestore_. DB users and roles are not included in the dump, unfortunately.  
Tough luck, unless you [read the friendly manual](https://en.wikipedia.org/wiki/RTFM#:~:text=the%20fine%20manual%22%2C%20%22-,read%20the%20friendly%20manual,-%22%2C%20%22read%20the%20%5Bpause) and see the [dumpDbUsersAndRoles](https://www.mongodb.com/docs/database-tools/mongodump/#std-option-mongodump.--dumpDbUsersAndRoles) flag.

Obtain standalone instance dump with:
```sh
mongodump --archive="cluster-dump.mongodump" --uri "mongodb+srv://USERNAME:<PASSWORD>@source.cbker.mongodb.net/"
```
obviously, [`--uri`](https://www.mongodb.com/docs/database-tools/mongodump/#std-option-mongodump.--uri) is the connection string to the source database. 
>⚠️ Mandatory disclaimers: It is not recommended to use the password in the command line as the command history are stored in `~/.*sh_history` files.  
You can omit the password and provide it interactively or you can use config file with [`--config`](https://www.mongodb.com/docs/database-tools/mongodump/#std-option-mongodump.--config) flag. 

`--archive` flag is used to make dump in a single file. Default behavior is to [dump to a directory](https://www.mongodb.com/docs/database-tools/mongodump/#dump-data-to-a-directory) with a mix of data and metadata files.






preliminary setup
creating local MongoDB replica set

mongodump & mongorestore
live migration of MongoDB data from one server to another
```sh
mongodump --archive="cluster-dump.mongodump" --uri "mongodb+srv://USERNAME:<PASSWORD>@source.cbker.mongodb.net/"
```

```sh 
mongodump --uri "mongodb+srv://muhammedcankucukaslan:***REMOVED***@source-cluster.cbker.mongodb.net/" --out ./tmp/mongodump
 
```

```sh
mongosync --cluster0 "mongodb+srv://muhammedcankucukaslan:***REMOVED***@source-cluster.cbker.mongodb.net/" --cluster1 "mongodb://localhost:27017"
```

https://www.mydbops.com/blog/mongodb-7-0-cluster-to-cluster-sync-simplifying-data-synchronization