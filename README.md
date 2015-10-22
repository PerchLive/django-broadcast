django-broadcast
======================================

[![Build Status](https://img.shields.io/travis/PerchLive/django-broadcast.svg)](https://travis-ci.org/PerchLive/django-broadcast) [![PyPI Page](https://img.shields.io/pypi/v/django-broadcast.svg)](https://pypi.python.org/pypi/django-broadcast) [![Coverage Status](https://img.shields.io/coveralls/PerchLive/django-broadcast.svg)](https://coveralls.io/github/PerchLive/django-broadcast?branch=master) [![Python Versions](https://img.shields.io/pypi/pyversions/django-broadcast.svg)](https://pypi.python.org/pypi/django-broadcast) [![Downloads per Day](https://img.shields.io/pypi/dd/django-broadcast.svg)](https://pypi.python.org/pypi/django-broadcast)


Overview
--------

Video broadcasting support for Django apps

API
---

These endpoints are all `POST`. Parameters are URL encoded for request, and JSON encoded for response.

## /stream/start/

#### Request (url encoded)

```
{
	'name' : 'some_name' (optional)
}

```

e.g: `https://endpoint.tld/stream/start/?name=my_stream_name`
	

#### Response (json encoded)

```javascript
{
	'stream' : {
		'id' : 'stream_id', (generally a UUID or similar)
		'name' : 'some_name',
		'start_date' : '2015-10-22 15:27:40', (time always in GMT)
	},
	'endpoint': {
		'S3': {
			'aws_access_key_id': 'key'
			'aws_secret_access_key': 'secret',
			'aws_session_token': 'token',
			'aws_expiration': 3600.0 // in seconds
			'aws_bucket_name': 'bucket',
			'aws_bucket_path': 'path',
			'aws_region': 'us-west-1' // valid amazon region string
		}
		// future endpoints could go here, like RTMP, WebRTC, etc
	}
}

```

## /stream/stop/

#### Request (url encoded)

```
{
	'id' : 'stream_id'
}

```
e.g: `https://endpoint.tld/stream/start/?id=B8C2401D-B2F8-47CD-90BD-53B608D47F3F`
	

#### Response (json encoded)

```
{
	'id' : 'stream_id',
	'name' : 'some_name',
	'start_date' : '2015-10-22 15:27:40', (time always in GMT)
	'stop_date' : '2015-10-22 16:27:40', (time always in GMT)
}

```

Requirements
------------

-  Python (2.7, 3.3, 3.4)
-  Django (1.6, 1.7, 1.8)
-  Django REST Framework (2.4, 3.0, 3.1)

Installation
------------

Install using `pip`

    $ pip install django-broadcast

Setup
-----

Currently django-broadcast supports an `S3` backend:

```python
BROADCAST_SETTINGS = {
    "S3": {
        "AWS_ACCESS_KEY" : "your_aws_access_key"
        "AWS_ACCESS_SECRET": "your_aws_access_secret"
    }
}

```

Testing
-------

Install testing requirements.

    $ pip install -r requirements.txt

Run with runtests.

    $ ./runtests.py

You can also use the excellent `tox`_ testing tool to run the tests
against all supported versions of Python and Django. Install tox
globally, and then simply run:


    $ tox
