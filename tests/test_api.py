from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import RequestFactory
from django_broadcast.api import start_hls_stream, stop_stream
from tests.conftest import TEST_S3_BUCKET, TEST_STREAM_MODEL
from tests.secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from api import prepare_hls_start_stream_response
from settings import STREAM_MODEL


class ApiTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testy', email='test@hotmail.com', password='asdf')

    def test_settings_configured(self):
        broadcast_settings = settings.BROADCAST_SETTINGS

        self.assertIsNotNone(broadcast_settings)
        self.assertIsNotNone(broadcast_settings['S3'])

        self.assertEqual(broadcast_settings['S3']['AWS_ACCESS_KEY_ID'], AWS_ACCESS_KEY_ID)
        self.assertEqual(broadcast_settings['S3']['AWS_SECRET_ACCESS_KEY'], AWS_SECRET_ACCESS_KEY)
        self.assertEqual(broadcast_settings['S3']['BUCKET'], TEST_S3_BUCKET)
        self.assertEqual(broadcast_settings['STREAM_MODEL'], TEST_STREAM_MODEL)

    def test_start_stop_hls_stream(self):
        test_stream_name = 'test_stream'
        rf = RequestFactory()
        start_request = rf.post('/stream/start/?name={}&type=hls'.format(test_stream_name))
        start_request.user = self.user

        '''
        Start Stream
        '''
        start_result = start_hls_stream(request=start_request)
        stream = start_result['stream']
        storage = start_result['storage']

        self.assertIsNotNone(stream)
        self.assertIsNotNone(storage)

        self.assertEqual(stream.name, test_stream_name)
        self.assertTrue(stream.is_live)

        start_response = prepare_hls_start_stream_response(start_result)
        # TODO : Assert Storage, Stream, response parameters are all valid

        '''
        Stop Stream
        '''
        stop_request = rf.post('/stream/stop/?id={}'.format(stream.id))
        stop_result = stop_stream(request=stop_request)

        self.assertIsNotNone(stop_result)
        self.assertEqual(stream.id, stop_result['id'])

        refreshed_stream = STREAM_MODEL.objects.get(id=stream.id)
        self.assertFalse(refreshed_stream.is_live)
