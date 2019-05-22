..
    This file is part of Invenio.
    Copyright (C) 2015-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Overview
========

In order to upload files, a Location needs to be defined first.
This will be the default location all buckets will have.
After having created the location, a bucket also needs to be created to hold
our file(s).
At this point a file can be uploaded, which will be represented by an
ObjectVersion inside an Object, linked to a FileInstance,
pointing to the actual location on disk.

Let's first describe the main concepts behind InvenioFilesREST:


Buckets
-------
Buckets act as containers for :code:`Objects`. They have a unique identifier,
and a default location and storage class.
However, the objects stored in the bucket can have different locations
and storage classes.
A bucket can also be marked as deleted, in which case the contents become
inaccessible, or can even be permanently removed,
which also deletes all :code:`Objects` it contains,
including their associated :code:`ObjectVersions`.
A bucket created with a certain size quota, which by default is unlimited,
and the bucket's size limit is determined by the default file size limiters.
The size of the bucked is determined by the size of
all Objects in the bucket (including all versions).


Bucket Tags
-----------
A bucket may have tags (key:value pairs) attached to it,
that one may use to store extra information.
The tags are identified uniquely within a bucket.


Objects
-------
Objects are an abstraction of a file, and are uniquely identified within
a bucket by string keys, i.e. the file name.


Object Versions
---------------
Object Versions represent versions of a file, and are uniquely identified
within an Object belonging to a Bucket.
An Object Version can be attached to one or more File Instances.
If no File Instance is attached, this means that the particular Object Version
was deleted (and is now a delete marker).
Additionally, multiple object versions can be pointing to the same file on disk
via File Instances
(useful for e.g. snapshotting a bucket without duplicating its contents).


File Instance
-------------
A file instance represents files on disk. One file instance can have many
objects linked to it.
