from django.http import HttpRequest
from django.contrib.auth.models import User
from storage_provisioner.storage import Storage
from storage_provisioner.provisioner import S3StorageProvisioner

import settings
from django_broadcast.models import HlsStream, Stream
from django_broadcast.serializers import HlsStreamSerializer

__author__ = 'dbro'

AWS_ACCESS_KEY_ID = settings.aws_access_key_id
AWS_SECRET_ACCESS_KEY = settings.aws_secret_access_key
S3_BUCKET_NAME = settings.s3_bucket
path_prefix_function = settings.STORAGE_PROVISIONER.path_prefix_function

PROVISIONER = S3StorageProvisioner(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def start_stream(request: HttpRequest) -> (Stream, Storage):
    stream_type = request.body['type']
    if stream_type is 'hls':
        return start_hls_stream(request)
    return None


def stop_stream(stream: Stream):
    stream.is_live = False
    # Maybe revoke storage tokens etc.

def start_hls_stream(request: HttpRequest) -> (Stream, Storage):

    deserialized_stream = HlsStreamSerializer(data=request.POST)

    PROVISIONER.provision_storage(user_name=request.user.username,
                                  bucket_name=S3_BUCKET_NAME,
                                  path=path_prefix_for_user(request.user))

    # TODO: Set the event / live manifest url?
    # We know the directory these files will live, but not necessarily what the client SDK
    # will call them. e.g: index.m3u8, ./dog/test.m3u8

    if deserialized_stream.is_valid():
        return deserialized_stream.instance
    return None


def path_prefix_for_user(user: User):
    """
    Return a path prefix relative to the root storage directory representing the user's accessible area.
    e.g: In S3, this corresponds to the path within the storage bucket where a user may read/write files.
    :param user: the Django user
    :return: a str path prefix. e.g: '33/'
    """

    # TODO : Perhaps this becomes a function on the user-supplied Stream model?
    return user.pk + '/'
