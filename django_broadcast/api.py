import datetime
import json

from django.core import serializers

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from storage_provisioner.provisioner import S3StorageProvisioner
from storage_provisioner.storage import S3Storage

from django_broadcast import settings
from django_broadcast.models import Stream

__author__ = 'dbro'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

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
    stream_type = request.GET.get('type')
    if stream_type is 'hls':
        return start_hls_stream(request)
    raise NotImplementedError


def stop_stream(request: HttpRequest) -> dict:
    stream_id = request.GET.get('id')
    if stream_id is None:
        raise KeyError

    stream = stream_model.objects.get(id=stream_id)
    stream.is_live = False
    stream.stop_date = datetime.datetime.utcnow()
    stream.save()
    return {'stream': stream}
    # Maybe revoke storage tokens etc.


def start_hls_stream(request: HttpRequest) -> dict:
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

    new_stream = stream_model.objects.create(owner=request.user,
                                             name=request.GET.get('name'),
                                             is_live=True)

    storage = PROVISIONER.provision_storage(user_name=request.user.username,
                                            bucket_name=S3_BUCKET_NAME,
                                            path=new_stream.storage_path())

    new_stream.event_manifest = storage.get_url_for_key(new_stream.storage_path('event.m3u8'))
    new_stream.live_manifest = storage.get_url_for_key(new_stream.storage_path('live.m3u8'))

    return {'stream': new_stream, 'storage': storage}


def prepare_start_hls_stream_response(start_hls_stream_response: dict) -> str:
    """
    Prepares an API response to be returned to the client based on the result of
    start_hls_stream.
    :param start_hls_stream_response: the result of start_hls_stream
    :return: a serialized string suitable for passing to the client
    """

    # We currently only support S3 storage backend
    if not isinstance(start_hls_stream_response['storage'], S3Storage):
        raise NotImplementedError

    # Stream is a Django Model : Use Django serializer
    # Serialize operates on an iterable
    serialized_stream = serializers.serialize('python',
                                              [start_hls_stream_response['stream']],
                                              fields=('id', 'name', 'start_date'))[0]
    # Django serializer returns {"id":...,"model":..., "fields":...}, but we just want a flat dict.
    serialized_stream = serialized_stream['fields']
    serialized_stream['id'] = start_hls_stream_response['stream'].id

    # Serialize datetimes with our specified stftime format.
    serialized_stream['start_date'] = serialized_stream['start_date'].strftime(DATE_FORMAT)

    # Storage is a pure python object: Use Python json serializer
    storage_dict = start_hls_stream_response['storage'].__dict__
    # Convert datetime to appropriate string format
    storage_dict['aws_expiration'] = storage_dict['aws_expiration'].utcnow().strftime(DATE_FORMAT)
    serialized_storage = json.dumps(storage_dict)

    return json.dumps({'stream': serialized_stream,
                       'endpoint': {'S3': serialized_storage}})


def prepare_stop_stream_response(stop_stream_response: dict) -> str:
    """
    Prepares an API response to be returned to the client based on the result of
    stop_stream.
    :param stop_stream_response: the result of stop_stream
    :return: a serialized string suitable for passing to the client
    """

    # Stream is a Django Model : Use Django serializer
    dict_serializer = serializers.get_serializer('python')()
    serialized_stream = dict_serializer.serialize([stop_stream_response['stream']],
                                                  fields=('id', 'name', 'start_date', 'stop_date'))[0]
    # Django serializer returns {"model":..., "fields":...}, but we just want fields.
    serialized_stream = serialized_stream['fields']
    serialized_stream['id'] = stop_stream_response['stream'].id

    # Serialize datetimes with our specified stftime format.
    serialized_stream['start_date'] = serialized_stream['start_date'].strftime(DATE_FORMAT)
    serialized_stream['stop_date'] = serialized_stream['stop_date'].strftime(DATE_FORMAT)

    return json.dumps({'stream': serialized_stream})
