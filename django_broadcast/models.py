from django.conf import settings

__author__ = 'dbro'

from django.db import models


class Thumbnail(models.Model):

    # streams M2M to Stream provided by Stream.thumbnails reverse relation
    timestamp = models.FloatField()
    image = models.URLField()


class Stream(models.Model):
    """
        The base representation of a video stream
    """

    name = models.CharField(max_length=255, blank=True, null=True)
    thumbnails = models.ManyToManyField(Thumbnail, related_name='streams')
    is_live = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)
    stop_date = models.DateTimeField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)

    def path_prefix(self):
        raise NotImplementedError

    class Meta:
        abstract = True

    def get_url(self) -> str:
        raise NotImplementedError

    def storage_path(self, filename=None) -> str:
        """
        Return a path prefix relative to the root storage directory representing this stream's storage area.
        If filename is specified, provide a path to filename within the stream's storage area.
        e.g: When using AWS S3, this corresponds to the path within the storage bucket where a user may read/write files.
        :param filename: (optional) the filename to concatenate to the stream's root storage area.
        :return: a str path prefix. The default implementation returns "<user_pk>/" or "<user_pk>/filename"
        """

        if filename:
            return "{}/{}/{}".format(self.owner.pk, self.pk, filename)
        return "{}/{}/".format(self.owner.pk, self.pk)


class HlsStream(Stream):
    """
        A representation of an HTTP-HLS stream
    """

    event_manifest = models.URLField()
    live_manifest = models.URLField()

    def get_url(self) -> str:
        return self.live_manifest if self.is_live else self.event_manifest
