__author__ = 'dbro'

from django.db import models


class Thumbnail(models.Model):

    stream = models.ForeignKey(Stream, related_name='thumbnails')
    timestamp = models.FloatField()
    image = models.URLField()


class Stream(models.Model):
    """
        The absolute base representation of a video stream
    """

    name = models.CharField(unique=True)
    # thumbnails provided by Thumbnail.stream reverse relation
    is_live = models.BooleanField()
    start_date = models.DateTimeField(auto_now_add=True)
    stop_date = models.DateTimeField(auto_now_add=True)

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
