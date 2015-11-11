from collections import OrderedDict
from rest_framework import serializers
from django_broadcast.models import HlsStream
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import SkipField

__author__ = 'dbro'


class NonNullSerializer:
    """
    Serializer mixin that removes None fields when converted to its externally-viewable representation
    Based off http://stackoverflow.com/a/28870066
    """

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is not None:
                represenation = field.to_representation(attribute)
                if represenation is None:
                    # Do not seralize empty objects
                    continue
                if isinstance(represenation, list) and not represenation:
                   # Do not serialize empty lists
                   continue
                ret[field.field_name] = represenation

        return ret


class HlsStreamSerializer(NonNullSerializer, ModelSerializer):

    #name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = HlsStream
        fields = ('name', 'start_date', 'stop_date')
        read_only_fields = ('start_date', 'stop_date')
