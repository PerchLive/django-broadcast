from django.conf import settings
from django.test import TestCase
from django.test import RequestFactory
from django_broadcast.api import start_hls_stream


class SettingsTestCase(TestCase):

    def test_settings_configured(self):

        self.assertIsNotNone(settings.BROADCAST_SETTINGS)

        test_stream_name = 'test_stream'
        rf = RequestFactory()
        request = rf.post('/stream/start', data={
            'name': test_stream_name
        })
        result = start_hls_stream(request=request)
        stream = result[0]
        storage = result[1]

        self.assertEqual(stream.name, test_stream_name)
