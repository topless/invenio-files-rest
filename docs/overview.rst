..
    This file is part of Invenio.
    Copyright (C) 2015-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


Overview
========
Invenio-Files-REST is a files storage module. It allows you to store and
retrieve files in a similar way to Amazon S3 APIs.

Before getting started a brief overview will introduce you to the key concepts
and terminology of the module.


Location
--------
The first concept to introduce is :code:`Location`. Locations are used to
represent different storage systems. :code:`Location` has a :code:`name` and a
:code:`URI` which could be a path in a local directory or a URI on a remote
system. It is required to have at least one Location.

See the API section of :py:class:`invenio_files_rest.models.Location` for more
information.


Storage
-------
Storage classes require a :code:`Location`, and they provide the interface to
interact with it. Storage works a programming interface for interacting with
files.

An example of a remote storage system, can be found at
`invenio-s3 <https://invenio-s3.readthedocs.io/>`_ which offers integration
with any S3 REST API compatible object storage.

See the API section of :py:class:`invenio_files_rest.storage` for more
information.


Bucket
------
Consider the :code:`Bucket` as a container for :code:`ObjectVersion` objects.

The :code:`Bucket` is identified by a unique ID and is created by default in
the default :code:`Location` with the default :code:`Storage` class unless you
provide specific ones.

For a file to be stored, we need to make sure we have created  a
:code:`Location` and a :code:`Bucket`.

.. .note::

    :code:`Objects` inside a :code:`Bucket` do not necessarily have the same
    :code:`Location` or :code:`Storage` class as the :code:`Bucket`.

A bucket can also be marked as deleted, in which case the contents become
inaccessible, or can even be permanently removed, which also deletes all
:code:`Objects` it contains, including their associated :code:`ObjectVersions`.

See the API section of :py:class:`invenio_files_rest.models.Bucket` for more
information.


BucketTag
-----------
:code:`BucketTag` is useful to store extra information for a :code:`Bucket`.
A :code:`BucketTag` is in the form of :code:`key: value` pair and a
:code:`Bucket` can have multiple :code:`BucketTag` uniquely identified by
their keys. It is common to address the collection of `BucketTag` of a
:code:`Bucket` as :code:`Bucket` metadata.

See the API section of :py:class:`invenio_files_rest.models.BucketTag` for more
information.


Object
------
An :code:`Object` is as an abstraction representation of a file, it doesn't
come its own model (database table) but it is represented through via the
:code:`ObjectVersion`. They are uniquely identified within a bucket by
string keys. An :code:`Object` can have multiple :code:`ObjectVersion`
pointing to it, useful for example for snapshotting a bucket without
duplicating its contents, this is achieve via the :code:`FileInstance`.
Just as in a computer files are contained inside folders, each :code:`Object`
has to be contained in a :code:`Bucket`.


ObjectVersion
-------------
An :code:`ObjectVersion` represents a version of a file, and is uniquely
identified within an Object. An :code:`ObjectVersion` is attached to one or
more :code:`FileInstance`. If no :code:`FileInstance` is attached to it, it
means that the particular :code:`ObjectVersion` was deleted (and is now a
delete marker).

The latest version of the file is referred to as the :code:`HEAD`, while a
version of the file is referred to as an :code:`ObjectVersion`.

See the API section of :py:class:`invenio_files_rest.models.ObjectVersion` for
more information.


FileInstance
------------
The actual link between an :code:`ObjectVersion` and the file on disk is made
by a :code:`FileInstance`. This allows for multiple :code:`ObjectVersion`
to point to the same :code:`FileInstance`, allowing some operations to be
performed more efficiently, such as snapshots without duplicating files or
migrating data.

See the API section of :py:class:`invenio_files_rest.models.FileInstance` for
more information.
