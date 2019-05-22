..
    This file is part of Invenio.
    Copyright (C) 2015-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Overview
========
Invenio-Files-REST is a files storage module. It allows you to store and retrieve
files in a similar way to Amazon S3 APIs.

In order to better understand what you can achieve with this Invenio module,
the following overview will introduce you to its key concepts and terminology.

In Invenio-Files-REST, a file is represented by an abstraction called :code:`Object`.
An Object acts like container for a particular file (as identified by its name),
and holds *it* as well as all its previous versions (if any). The latest version
of the file is referred to as the :code:`HEAD`, while a version of the file is
referred to as an :code:`Object Version`. The link between an :code:`Object Version`
and the actual file on disk is made by a :code:`File Instance`. What this allows
is for multiple :code:`Object Versions` to point to the same :code:`File Instance`,
allowing some operations to be performed more efficiently, such as snapshots
without duplicating files or migrating data.
Just as in a computer files are contained inside folders, each :code:`Object` has
to be contained in a :code:`Bucket`. The bucket is identified by a unique ID,
assigned automatically at creation. A :code:`Bucket` is created by default in the
default :code:`Location`, however that can be changed such that when creating a
:code:`Bucket`, a particular :code:`Location` for it can be specified. The
:code:`Bucket` can also have a maximum quota assigned to it, and an important
point to note is that the :code:`Objects` inside it do not necessarily have to
be located in the same :code:`Location`. The :code:`Location` can be used to
represent various storage systems and/or various geo-locations.

Thus, for a file to be stored, we need to make sure we have defined at least a
default :code:`Location`, as well as a :code:`Bucket` for that location.


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
