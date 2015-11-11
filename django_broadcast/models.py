from django.contrib.auth.models import User

__author__ = 'dbro'

from django.db import models


class Stream(models.Model):
    """
        The base representation of a video stream
    """

    name = models.CharField(unique=True, max_length=255)
    # thumbnails provided by Thumbnail.stream reverse relation
    is_live = models.BooleanField()
    start_date = models.DateTimeField(auto_now_add=True)
    stop_date = models.DateTimeField()
    owner = models.ForeignKey(User)

    def path_prefix(self):
        raise NotImplementedError

    class Meta:
        abstract = True

    def get_url(self) -> str:
        raise NotImplementedError


class HlsStream(Stream):
    """
        A representation of an HTTP-HLS stream
    """

    event_manifest = models.URLField()
    live_manifest = models.URLField()

    def get_url(self) -> str:
        return self.live_manifest if self.is_live else self.event_manifest


class Thumbnail(models.Model):

    # TODO : Can't have a ForeignKey to an abstract class
    # Instead see https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/#generic-relations
    stream = models.ForeignKey(Stream, related_name='thumbnails')
    timestamp = models.FloatField()
    image = models.URLField()
