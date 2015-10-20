django-broadcast
======================================

|build-status-image| |pypi-version|

Overview
--------

Video broadcasting support for Django apps

Requirements
------------

-  Python (2.7, 3.3, 3.4)
-  Django (1.6, 1.7, 1.8)
-  Django REST Framework (2.4, 3.0, 3.1)

Installation
------------

Install using ``pip``\ …

.. code:: bash

    $ pip install django-broadcast

Setup
-----

Currently django-broadcast supports an `S3` backend:

```python
BROADCAST_SETTINGS = {
    "S3": {
        "AWS_ACCESS_KEY" : "your_aws_access_key"
        "AWS_ACCESS_SECRET": "your_aws_access_secret"
        "DEFAULT_POLICY": "your_default_s3_policy"
    }
}

```

An example value for `DEFAULT_POLICY`:

```json
{
   "Version":"2012-10-17",
   "Statement":[
      {
         "Effect":"Allow",
         "Action":[
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:PutObjectAclVersion",
            "s3:GetObject",
            "s3:GetObjectVersion",
            "s3:DeleteObject",
            "s3:DeleteObjectVersion"
         ],
         "Resource":"arn:aws:s3:::BUCKET_NAME/PATH/*"
      },
      {
         "Effect":"Allow",
         "Action":[
            "s3:ListBucket",
            "s3:GetBucketLocation",
            "s3:ListAllMyBuckets"
         ],
         "Resource":"arn:aws:s3:::BUCKET_NAME/PATH"
      }
   ]
}
```

Testing
-------

Install testing requirements.

.. code:: bash

    $ pip install -r requirements.txt

Run with runtests.

.. code:: bash

    $ ./runtests.py

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:

.. code:: bash

    $ tox

.. _tox: http://tox.readthedocs.org/en/latest/

.. |build-status-image| image:: https://secure.travis-ci.org/OnlyInAmerica/django-broadcast.svg?branch=master
   :target: http://travis-ci.org/OnlyInAmerica/django-broadcast?branch=master
.. |pypi-version| image:: https://img.shields.io/pypi/v/django-broadcast.svg
   :target: https://pypi.python.org/pypi/django-broadcast
