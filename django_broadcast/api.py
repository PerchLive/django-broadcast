import datetime

from django.core import serializers

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from storage_provisioner.provisioner import S3StorageProvisioner
from storage_provisioner.storage import S3Storage

from django_broadcast import settings
from django_broadcast.models import HlsStream, Thumbnail

__author__ = 'dbro'


AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
S3_BUCKET_NAME = settings.s3_bucket
stream_model = settings.STREAM_MODEL
PROVISIONER = S3StorageProvisioner(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def start_stream(request: HttpRequest) -> dict:
    """
    Prepare for a new stream on behalf of the request's author. This involves
    provisioning remote storage for the stream media and returning any necessary
    data for the streaming client.
    :param request:
    :return:
    """
    stream_type = request.POST.get('type')
    if stream_type is 'hls':
        return start_hls_stream(request)
    raise NotImplementedError


def stop_stream(request: HttpRequest) -> dict:
    stream_id = request.POST.get('id')
    if stream_id is None:
        raise KeyError

    stream = stream_model.objects.get(id=stream_id)
    stream.is_live = False
    stream.stop_date = datetime.datetime.utcnow()
    stream.save()
    return {'stream': stream}
    # Maybe revoke storage tokens etc.


def start_hls_stream(request: HttpRequest, stream: HlsStream) -> dict:
    """
    Create credentials to for a new HTTP-HLS Stream. This method
    requires that the request corresponds to an authenticated user and
    has been processed by Django's Authentication middleware.
    :param request: the request issued by an authenticated user.
    :return: a dict of the following form:
        { "stream" : Stream, "storage": Storage }
    """

    if not request.user or not request.user.is_authenticated():
        raise PermissionDenied

    stream.is_live = True

    storage = PROVISIONER.provision_storage(user_name=request.user.username,
                                            bucket_name=S3_BUCKET_NAME,
                                            path=stream.storage_path())

    stream.event_manifest = storage.get_url_for_key(stream.storage_path('vod.m3u8'))
    stream.live_manifest = storage.get_url_for_key(stream.storage_path('index.m3u8'))

    thumbnail_path = storage.get_url_for_key(stream.storage_path('thumb.jpg'))
    thumbnail = Thumbnail.objects.create(timestamp = 0, image = thumbnail_path)

    stream.thumbnails.add(thumbnail)

    stream.save()

    return {'stream': stream, 'storage': storage}


def prepare_start_hls_stream_response(start_hls_stream_response: dict) -> dict:
    """
    Prepares an API response to be returned to the client based on the result of
    start_hls_stream.
    :param start_hls_stream_response: the result of start_hls_stream
    :return: a serialized string suitable for passing to the client
    """

    # We currently only support S3 storage backend
    if not isinstance(start_hls_stream_response['storage'], S3Storage):
        raise NotImplementedError

    stream = start_hls_stream_response['stream']
    serialized_stream = {}
    serialized_stream['id'] = stream.id
    serialized_stream['name'] = stream.name
    # Serialize datetimes with our specified stftime format.
    serialized_stream['start_date'] = stream.start_date

    # Storage is a pure python object
    storage_dict = start_hls_stream_response['storage'].__dict__
    # Convert datetime to appropriate string format
    storage_dict['aws_expiration'] = storage_dict['aws_expiration'].utcnow()


    return {'stream': serialized_stream,
            'endpoint': {'S3': storage_dict}}


def prepare_stop_stream_response(stop_stream_response: dict) -> dict:
    """
    Prepares an API response to be returned to the client based on the result of
    stop_stream.
    :param stop_stream_response: the result of stop_stream
    :return: a serialized string suitable for passing to the client
    """

    # Stream is a Django Model : Use Django serializer
    serialized_stream = {}
    serialized_stream['id'] = stop_stream_response['stream'].id
    serialized_stream['name'] = stop_stream_response['stream'].name
    serialized_stream['start_date'] = stop_stream_response['stream'].start_date
    serialized_stream['stop_date'] = stop_stream_response['stream'].stop_date

    return {'stream': serialized_stream}
