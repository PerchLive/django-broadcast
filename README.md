django-broadcast
======================================

[![Build Status](https://img.shields.io/travis/PerchLive/django-broadcast.svg)](https://travis-ci.org/PerchLive/django-broadcast) [![PyPI Page](https://img.shields.io/pypi/v/django-broadcast.svg)](https://pypi.python.org/pypi/django-broadcast) [![Coverage Status](https://img.shields.io/coveralls/PerchLive/django-broadcast.svg)](https://coveralls.io/github/PerchLive/django-broadcast?branch=master) [![Python Versions](https://img.shields.io/pypi/pyversions/django-broadcast.svg)](https://pypi.python.org/pypi/django-broadcast) [![Downloads per Day](https://img.shields.io/pypi/dd/django-broadcast.svg)](https://pypi.python.org/pypi/django-broadcast)


Overview
--------

Video broadcasting support for Django apps. Designed to abstract provisioning backend storage for video streaming clients behind
simple "Start Stream" and "Stop Stream" API calls.

API
---

These endpoints are all `POST`. Parameters are URL encoded for request, and JSON encoded for response.

## /stream/start/

#### Request (url encoded)

```
{
    'type' : 'hls' (this is the only option currently supported)
	'name' : 'some_name' (optional)
}

```

e.g: `https://endpoint.tld/stream/start/?name=some_name&type=hls`
	

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
			's3_bucket_name': 'bucket',
			's3_bucket_path': 'path',
			's3_bucket_region': 'us-west-1' // valid amazon region string
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

```javascript
{
    'stream': {
        'id' : 'stream_id',
        'name' : 'some_name',
        'start_date' : '2015-10-22 15:27:40', (time always in GMT)
        'stop_date' : '2015-10-22 16:27:40', (time always in GMT)
    }
}

```

Usage
---
We currently recommend your hosting Django application setup the URL and views for `/stream/start` and `/stream/stop`.
Within those views, you can yield to built-in methods to handle most of the work for you while leaving you ultimate control
over the request and response formats.

For example, your `/stream/start` view may look like:

```python

    from django.http import JsonResponse
    from django_broadcast.api import start_hls_stream, prepare_start_hls_stream_response

    def your_start_stream_view(request):

        # Do request validation, etc.

        # Prepare for new Stream : This handles creating storage credentials
        # and preparing data needed by mobile client
        start_result = start_hls_stream(request=request)
        # start_result is a python dictionary with format:
        # {'stream': ..., 'storage': ...}

        # Use built-in function for standard dictionary representation
        # as specified in API section above.
        serialized_response = prepare_start_hls_stream_response(start_result)

        return JsonResponse({'success': true, 'response': serialized_response})

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
    "STREAM_MODEL": "home.Stream",
    "S3": {
        "AWS_ACCESS_KEY_ID": os.environ.get('DJ_BROADCAST_AWS_ACCESS_KEY', ''),
        "AWS_SECRET_ACCESS_KEY": os.environ.get('DJ_BROADCAST_AWS_ACCESS_SECRET', ''),
        "BUCKET": os.environ.get('DJ_BROADCAST_S3_BUCKET', '')
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
