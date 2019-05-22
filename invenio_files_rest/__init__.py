# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


r"""REST API for Files.

Invenio-Files-REST provides configurable REST APIs for uploading, serving,
downloading and deleting files. It works as a standalone module or in
combination with `Invenio-Records <https://invenio-records.readthedocs.io>`_
through the
`Invenio-Records-Files <https://invenio-records-files.readthedocs.io>`_
integration.

The module can be configured with different storage backends, and provides
features such as:

- A robust REST API.
- Configurable storage backends with the ability to build your very own.
- Highly customizable access-control.
- Secure file handling.
- Integrity checking mechanism.
- Support for large file uploads and multipart upload.
- Signals for system events.

The REST API follows best practices and supports, e.g.:

- Content negotiation and links headers.
- Cache control via ETags and Last-Modified headers.
- Optimistic concurrency control via ETags.
- Rate-limiting, Cross-Origin Resource Sharing, and various security headers.


Initialization
--------------
First, let's create the flask application:

>>> from flask import Flask
>>> app = Flask('myapp')

Now to configure our application:

>>> app.config['BROKER_URL'] = 'redis://'
>>> app.config['CELERY_RESULT_BACKEND'] = 'redis://'
>>> app.config['DATADIR'] = 'data'
>>> app.config['FILES_REST_MULTIPART_CHUNKSIZE_MIN'] = 4
>>> app.config['REST_ENABLE_CORS'] = True
>>> app.config['SECRET_KEY'] = 'CHANGEME'
>>> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
>>> app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
>>> app.config['FILES_REST_PERMISSION_FACTORY'] = \
        lambda: type('Allow', (), {'can': lambda self: True})()


Now let's initialize all required Invenio extensions:

>>> import shutil
>>> from os import makedirs
>>> from os.path import dirname, exists
>>> from pprint import pprint
>>> import json

>>> from flask_babelex import Babel
>>> from flask_menu import Menu
>>> from invenio_db import InvenioDB, db
>>> from invenio_rest import InvenioREST
>>> from invenio_admin import InvenioAdmin
>>> from invenio_accounts import InvenioAccounts
>>> from invenio_access import InvenioAccess
>>> from invenio_accounts.views import blueprint as accounts_blueprint
>>> from invenio_celery import InvenioCelery
>>> from invenio_files_rest import InvenioFilesREST
>>> from invenio_files_rest.views import blueprint
>>> from invenio_files_rest.models import Location

>>> Babel(app)
>>> Menu(app)
>>> InvenioDB(app)
>>> InvenioREST(app)
>>> InvenioAdmin(app)
>>> InvenioAccounts(app)
>>> InvenioAccess(app)

Finally, let's initialize InvenioFilesREST, register the blueprints
and push a Flask application context:

>>> InvenioFilesREST(app)

>>> app.register_blueprint(accounts_blueprint)
>>> app.register_blueprint(blueprint)

>>> app.app_context().push()

Let's create the database and tables, using an in-memory SQLite database:

>>> db.create_all()

>>> srcroot = dirname(dirname(__file__))
>>> d = app.config['DATADIR']
>>> if exists(d):
>>>     shutil.rmtree(d)
>>> makedirs(d)

There's also a need to create a location for the buckets:

>>> loc = Location(name='local', uri=d, default=True)
>>> db.session.add(loc)
>>> db.session.commit()

Now let's create a bucket:

>>> res = app.test_client().post('/files')

And see the response containing the id of the bucket:

>>> pprint(json.loads(res.get_data().decode("utf-8")))


REST API Overview
-----------------

This part of the documentation will show you how to get started in using the
REST API of Invenio-Files-REST.

.. note::
    Note that the api is exposed from :code:`/files/` and is registered as a
    blueprint_api which means in our wrapper application will be prefixed with
    :code:`/api/`. That means that our api will be exposed in our application
    under :code:`/api/files/`.


About the API
-------------

The REST API allows you to create buckets and perform CRUD operations on files.
You can use query parameters in order to perform these operations.


Available methods and endpoints
-------------------------------

By default, the URL prefix for the REST API is under /files.

HEAD
^^^^

Check if bucket exists, returning either a 200 or a 404:

.. code-block:: console

    HEAD /files/<bucket_id>

GET
^^^

Return list of files in bucket:

.. code-block:: console

    GET /files/<bucket_id>/

Return list of file versions:

.. code-block:: console

    GET /files/<bucket_id>?versions

Return list of multipart uploads:

.. code-block:: console

    GET /files/<bucket_id>?uploads

Download file:

.. code-block:: console

    GET /files/<bucket_id>/<file_name>

Return list of parts of a multipart upload:

.. code-block:: console

    GET /files/<bucket_id>/<file_name>?uploadId=<id_number>


PUT
^^^

Upload file:

.. code-block:: console

    PUT /files/<bucket_id>/<file_name>

Upload part of in-progress multipart upload:

.. code-block:: console

    PUT /files/<bucket_id>/<file_name>?uploadId=<id_number>&part=<part_number>

POST
^^^^

Create a bucket:

.. code-block:: console

    POST /files/docs

Initiate multipart upload:

.. code-block:: console

    POST /files/<bucket_id>/<file_name>?
         uploads&size=<total_size>&partSize=<part_size>

Finalize multipart upload:

.. code-block:: console

    POST /files/<bucket_id>/<file_name>?uploadId=<id_number>

DELETE
^^^^^^
Permanently erase file version:

.. code-block:: console

    DELETE /files/<bucket_id>/<file_name>?versionId=<version_id>

Mark whole file as deleted:

.. code-block:: console

    DELETE /files/<bucket_id>/<file_name>

Abort multipart upload:

.. code-block:: console

    DELETE /files/<bucket_id>/<file_name>?uploadId=<upload_id>


Storage Backends
----------------
In order to get started let's setup and configure a storage backend.
Storage will serve as an interface for the actual file access.

In the configuration of the application, the variable
:py:data:`invenio_files_rest.config.FILES_REST_STORAGE_FACTORY`
defines the path of the factory that will be used to create a storage instance.
Each file instance uses the storage factory to create a storage interface for
itself.

Under the hood the module uses `PyFilesystem <https://www.pyfilesystem.org/>`_
to save files. This file system abstraction gives us the flexibility to be able
to swap storages very easy. The storage backend can also be a cloud service, as
an example you can have a look at
`invenio-s3 <https://invenio-s3.readthedocs.io/>`_ which offers integration
with any S3 REST API compatible object storage.


Build your own Storage Backend
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Advanced topic on how to implement and connect your own storage Backend for
Invenio-Files-REST.

In order to use a different storage backend, its required to subclass the
:py:data:`invenio_files_rest.storage.FileStorage` class, and provide
implementations for some of its methods:

Mandatory methods to implement:

* :code:`initialize`
* :code:`open`
* :code:`save`
* :code:`update`
* :code:`delete`

Optional methods to implement:

* :code:`send_file`
* :code:`checksum`
* :code:`copy`
* :code:`_init_hash`
* :code:`_compute_checksum`
* :code:`_write_stream`


Create Buckets
--------------

In order to upload, modify or delete files, a bucket needs to be created first.
A bucket can be created by a POST request to the url prefix, i.e. /files.
The response will contain the unique ID of the bucket.
A bucket can have one or more tags which store extra metadata for that bucket.
Each tag is uniquely identified by a key.

First let's create a bucket:

.. code-block:: console

   $ curl -X POST http://localhost:5000/files

.. code-block:: json

    {
        "max_file_size": null,
        "updated": "2019-05-16T13:07:21.595398+00:00",
        "locked": false,
        "links": {
            "self": "http://localhost:5000/files/
                     cb8d0fa7-2349-484b-89cb-16573d57f09e",
            "uploads": "http://localhost:5000/files/
                        cb8d0fa7-2349-484b-89cb-16573d57f09e?uploads",
            "versions": "http://localhost:5000/files/
                         cb8d0fa7-2349-484b-89cb-16573d57f09e?versions"
        },
        "created": "2019-05-16T13:07:21.595391+00:00",
        "quota_size": null,
        "id": "cb8d0fa7-2349-484b-89cb-16573d57f09e",
        "size": 0
    }


Upload Files
------------

The REST API allows you to upload, download and modify single files.
A file is uniquely identified within a bucket by its name.
Each file can have multiple versions.

Let's upload a file called my_file.txt inside the bucket that was just created.
To do this, the PUT command needs to be used, and the bucket ID as well
as the file ("my_file.txt") need to be specified.

Upload a file:

.. code-block:: console

   $ B=cb8d0fa7-2349-484b-89cb-16573d57f09e

   $ curl -i -X PUT --data-binary @my_file.txt \
     "http://localhost:5000/files/$B/my_file.txt"

.. code-block:: json

    {
        "mimetype": "text/plain",
        "updated": "2019-05-16T13:10:22.621533+00:00",
        "links": {
            "self": "http://localhost:5000/files/
                     cb8d0fa7-2349-484b-89cb-16573d57f09e/my_file.txt",

            "version": "http://localhost:5000/files/
                        cb8d0fa7-2349-484b-89cb-16573d57f09e/my_file.txt?
                        versionId=7f62676d-0b8e-4d77-9687-8465dc506ca8",
            "uploads": "http://localhost:5000/files/
                        cb8d0fa7-2349-484b-89cb-16573d57f09e/
                        my_file.txt?uploads"
        },
        "is_head": true,
        "tags": {},
        "checksum": "md5:d7d02c7125bdcdd857eb70cb5f19aecc",
        "created": "2019-05-16T13:10:22.617714+00:00",
        "version_id": "7f62676d-0b8e-4d77-9687-8465dc506ca8",
        "delete_marker": false,
        "key": "my_file.txt",
        "size": 14
    }

Should you want to update the same file with a new version you would use the
same command. Automatically, the file will be versioned.


JS Uploaders
^^^^^^^^^^^^

There are a wide variety of JavaScript uploaders which could be used with
Invenio-Files-REST. There is a possibility that the uploader might not work
out of the box due to the fact that Invenio-Files-REST expects the submitted
parameters to map to specific names.

An example of a mapping like this can be found at
:py:func:`invenio_files_rest.views.ngfileupload_uploadfactory` for the
`ng-file-upload <https://github.com/danialfarid/ng-file-upload>`_ angular
uploader. You can extend the upload factories according to your needs by
providing your implementations in the following :code:`config` variables.

1. Assing your factories to the :code:`config` variables:
:py:data:`invenio_files_rest.config.FILES_REST_MULTIPART_PART_FACTORIES` and
:py:data:`invenio_files_rest.config.FILES_REST_UPLOAD_FACTORIES`

2. Use the :code:`@use_kwargs` decorator to map your JS upoader's parameters
to :code:`content_length`, :code:`content_type`, :code:`uploaded_file` and
:code:`file_tags_header`


Multipart Upload
^^^^^^^^^^^^^^^^

In some cases, a file may be too large for a single upload. Or you may want to
speed up the upload process by uploading multiple parts in parallel. In these
cases, you have to use multipart uploads. This requires that each part is the
same size, except for the last one. Once all parts have been uploaded, the
multipart upload completes, and the parts are merged into one single file. At
this, point, it is no longer possible to upload new parts. When uploading a
multipart file, if one of the chunks fails, the database is rolled back and
the part is deleted.

.. note:
    **NOTE:** The last part needs to be less than or equal to the previous n-1
    parts.

As an example, let's create an 11MB file which will then be split into 2
chunks using the linux :code:`split` command:

.. code-block:: console

   dd if=/dev/urandom of=my_file.txt bs=1048576 count=11

   split -b6291456 my_file.txt segment_

To initialize a multipart upload, the POST command has to be used,
and to specify the fact that it is a multipart upload, the "uploads" query
parameter is used. Additionally, the total size and the part size need to be
specified.

Create a new bucket:

.. code-block:: console

   $ curl -X POST http://localhost:5000/files

The ID is contained in the response:

.. code-block:: json

    {
       "max_file_size":null,
       "updated":"2019-05-17T06:52:52.897378+00:00",
       "locked":false,
       "links":{
          "self":"http://localhost:5000/files/
                  c896d17b-0e7d-44b3-beba-7e43b0b1a7a4",
          "uploads":"http://localhost:5000/files/
                     c896d17b-0e7d-44b3-beba-7e43b0b1a7a4?uploads",
          "versions":"http://localhost:5000/files/
                      c896d17b-0e7d-44b3-beba-7e43b0b1a7a4?versions"
       },
       "created":"2019-05-17T06:52:52.897373+00:00",
       "quota_size":null,
       "id":"c896d17b-0e7d-44b3-beba-7e43b0b1a7a4",
       "size":0
    }

.. code-block:: console

   $ B=c896d17b-0e7d-44b3-beba-7e43b0b1a7a4

   $ curl -i -X POST \
     "http://localhost:5000/files/$B/my_file.txt?
      uploads&size=11534336&partSize=6291456"

.. code-block:: json

    {
       "updated":"2019-05-17T07:07:22.219002+00:00",
       "links":{
          "self":"http://localhost:5000/files/
                  c896d17b-0e7d-44b3-beba-7e43b0b1a7a4/my_file.txt?
                  uploadId=a85b1cbd-4080-4c81-a95c-b4df5d1b615f",

          "object":"http://localhost:5000/files/
                    c896d17b-0e7d-44b3-beba-7e43b0b1a7a4/my_file.txt",

          "bucket":"http://localhost:5000/files/
                    c896d17b-0e7d-44b3-beba-7e43b0b1a7a4"
       },
       "last_part_size":5242880,
       "created":"2019-05-17T07:07:22.218998+00:00",
       "bucket":"c896d17b-0e7d-44b3-beba-7e43b0b1a7a4",
       "completed":false,
       "part_size":6291456,
       "key":"my_file.txt",
       "last_part_number":1,
       "id":"a85b1cbd-4080-4c81-a95c-b4df5d1b615f",
       "size":11534336
    }

Continue uploading parts, by using the PUT command and specifying the id of
the bucket:

.. code-block:: console

   $ U=a85b1cbd-4080-4c81-a95c-b4df5d1b615f

   $ curl -i -X PUT --data-binary @segment_aa \
     "http://localhost:5000/files/$B/my_file.txt?uploadId=$U&partNumber=0"

    {
       "updated":"2019-05-17T07:08:27.069504+00:00",
       "created":"2019-05-17T07:08:27.048028+00:00",
       "checksum":"md5:876ae993a752f38b1850668be7e3fe9a",
       "part_number":0,
       "end_byte":6291456,
       "start_byte":0
    }

   $ curl -i -X PUT --data-binary @segment_ab \
     "http://localhost:5000/files/$B/my_file.txt?uploadId=$U&partNumber=1"

Complete a multipart upload, by using the POST command; it will return a 200
code on success:

.. code-block:: console

   $ curl -i -X POST \
     "http://localhost:5000/files/$B/my_file.txt?uploadId=$U"

Abort a multipart upload (deletes all uploaded parts); it will return a 204
code if it succeeds:

.. code-block:: console

   $ curl -i -X DELETE "http://localhost:5000/files/$B/my_file.txt?uploadId=$U"

Large Files
^^^^^^^^^^^

For smaller files, uploads are stored in the webserver's memory.
As for larger files, they are stored in a temporary location.
You will need some extra configurations for nginx and Flask application.

1. There is a possibility that Ngxinx might return
:code:`413 (Request Entity Too Large)` for large files. In the configuration
the body size of the request can be customized according to our needs. The
following example configures nginx to accept up to :code:`25MB`.

.. code-block:: console

    http {
        ...
        client_max_body_size 25M;
    }

2. Specify :code:`MAX_CONTENT_LENGTH` header otherwise Flask will reject
incoming requests with a content length greater than this by returning a
:code:`413 (Request Entity Too Large)`. If not set and the request does not
specify a :code:`CONTENT_LENGTH`, no data will be read for security. You can
set the :code:`MAX_CONTENT_LENGTH` to :code:`25MB`  like in the example below.

.. code-block:: console

    $ app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024

.. note::

    Special note on the :code:`get_data()` method: Calling this loads the full
    request data into memory. This is only safe to do if the
    :code:`max_content_length` is set.


Retrieve Files
--------------
Once the bucket is created and a file is uploaded, it is possible
to retrieve it with a GET request.

By default, the latest version will be downloaded. To retrieve a specific
version of the file, the versionId query parameter can be used, as in the
example below:

Download the latest version of the file:

.. code-block:: console

   $ curl -i http://localhost:5000/files/$B/my_file.txt

Download a specific version of the file:

.. code-block:: console

   $ curl -i http://localhost:5000/files/$B/my_file.txt?versionId=<version_id>

**NOTE:** By default, the file is returned with the header
:code:`'Content-Disposition': 'inline'`, so that the browser will try to
preview it. In case you want to trigger a download of the file, use the
:code:`download` query parameter, which will change the
:code:`'Content-Disposition'` header to :code:`'attachment'`

.. code-block:: console

   $ curl -i http://localhost:5000/files/$B/my_file.txt?download


Security
^^^^^^^^
It is very easy to be exposed to Cross-Site Scripting (XSS) attacks if you
serve user uploaded files. Here are some recommendations:

1. Serve user uploaded files from a separate domain (not a subdomain). This
way a malicious file can only attack other user uploaded files.

2. Prevent the browser from rendering and executing HTML files by setting
trusted=False.

3. Force the browser to download the file as an attachment (as_attachment=True)
by adding the :code:`download` keyword in the query parameters.


Delete Files
------------

If you want to delete a file there are two options:

1. Permanently erase a specific file version from the disk by specifying
the version id:

.. code-block:: console

   $ curl -i -X DELETE \
       http://localhost:5000/files/$B/my_file.txt?versionId=<version_id>

2. Delete a whole file (creates a delete marker which makes the file
inaccessible):

.. code-block:: console

   $ curl -i -X DELETE http://localhost:5000/files/$B/my_file.txt


Access control
--------------

Invenio-Files-REST depends on `Invenio-Access
<https://invenio-access.readthedocs.io>`_ module, to control the files access.

It comes with a default permission factory implementation which can be found
at :py:data:`invenio_files_rest.permissions.permission_factory` and can be
customized further, by providing our custom implementation in the relevant
config variable
:py:data:`invenio_files_rest.config.FILES_REST_PERMISSION_FACTORY`.

The module also comes with a list of predefined actions for the most common
operations:

    - location-update
    - bucket-read
    - bucket-read-versions
    - bucket-update
    - bucket-listmultiparts
    - object-read
    - object-read-version
    - object-delete
    - object-delete-version
    - multipart-read
    - multipart-delete


The aforementioned actions accept parameters, and can be simply applied by
decorating our desired function. For example, to verify that the contents of
a bucket can be read, you should have the bucket-read permission which takes
the bucket as the argument.

.. code-block:: python

    @need_permissions(
        lambda self, bucket, versions: bucket,
        'bucket-read',
    )
    def my_function():
        pass

.. note::

    (This is mentioned in the code, not sure if should go here)
    The actual file access is handled by the storage interface.

See :mod:`invenio_files_rest.permissions` for extensive documentation.


Integrity
---------

Invenio-Files-REST stores file checksums and regularly revalidates them, in
order to verify the data integrity of all data at rest, as well as to detect
corruption of data in transit.

Whenever an operation like :code:`merge_multipartobject` the database is rolled
back to reflect the state of the system before the action.

For the computation of the checksum you can provide the desired algorithm,
otherwise :code:`MD5` will be used.

In the case of trying to remove a file, the expectation is for the
FileInstance removal to succeed in the database so that afterwards
it's possible to proceed with the removal of the actual file. By binding the
actions together, in case of database operation error, you can prevent the
system ending up with orphan files. Some of the tasks support :code:`silent`
as an argument to prevent propagation of the errors.

There is also a predefined task :code:`verify_checksum` which can be configured
to run periodically (default is every 30 days) which iterates all files in our
storage and validates their checksum.

>>> "Get the checksum of an uploaded file for demo"

Signals
-------
Invenio-Files-REST supports signals that can be used to react to events.

Events are sent in case of:

* file downloaded

Let's request to download a file, and capture the signal:

>>> from invenio_files_rest.signals import file_downloaded

>>> def after_file_downloaded(send, *args, *kwargs):
...     print('Signal file_downloaded emitted')
...
>>> listener = file_downloaded.connect(after_file_downloaded)
>>> # Request to dowload a file for the event to trigger

You can read more about the `Flask Signals
<http://flask.pocoo.org/docs/1.0/signals/>`_.


Data Migration
--------------

:code:`Locations` are used to represent different storage systems and possibly
different geographical locations. :code:`Buckets` but also :code:`Objects` are
assigned a Location. This approach provides extra flexibility when there's
a need to migrate the data.

When a bucket is created, a Location needs to be provided, otherwise the
default one is used.

.. note::
    Before updating our records to point to the new :code:`Location`, the
    actual files need to be copied in the new storage with the new location.
    Then a bulk update needs to be performed on the FileInstance objects
    to point to the new bucket.

Invenio-Files-REST provides a celery task
:py:func:`invenio_files_rest.tasks.migrate_file` to migrate existing files
from current location to a new location. A new location might be in remote
system on a different bucket, even on a different storage backend. This task
can be used to migrate all files or a subset of files in case of location
change. Given a :code:`file_id` and the name of the new location (which should
have been already created), it will:

    1. create a new empty :code:`FileInstance` in the destination location
    2. copy the file content in the newly created :code:`FileInstance`
    3. re-link all ObjectVersions pointing to the previous :code:`FileInstance`
       to the new one, and optionally with :code:`post_fixity_check` argument,
       re-compute the file checksum

In case process does not complete successfully, destination
:code:`FileInstance` is removed completely and the process has to be repeated.

See :doc:`api` for an extensive API documentation.
"""

from __future__ import absolute_import, print_function

from .ext import InvenioFilesREST
from .proxies import current_files_rest
from .version import __version__

__all__ = ('__version__', 'current_files_rest', 'InvenioFilesREST', )
