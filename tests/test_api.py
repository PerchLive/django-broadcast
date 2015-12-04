import json
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import RequestFactory
from tests.conftest import TEST_S3_BUCKET, TEST_STREAM_MODEL
from tests.secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from api import start_hls_stream, stop_stream, prepare_start_hls_stream_response, prepare_stop_stream_response, DATE_FORMAT
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

        start_response = prepare_start_hls_stream_response(start_result)
        start_response_dict = json.loads(start_response)
        self.assertEqual(stream.id, start_response_dict['stream']['id'])
        self.assertEqual(stream.name, start_response_dict['stream']['name'])
        self.assertEqual(datetime.strftime(stream.start_date, DATE_FORMAT),
                         start_response_dict['stream']['start_date'])

        self.assertIsNotNone(start_response_dict['endpoint']['S3'])
        # Testing the validity of storage credentials is handled by storage_provisioner tests

        '''
        Stop Stream
        '''
        stop_request = rf.post('/stream/stop/?id={}'.format(stream.id))
        stop_result = stop_stream(request=stop_request)

        self.assertIsNotNone(stop_result)

        # Re-query Stream model to pickup changes made by stop_stream
        stream = STREAM_MODEL.objects.get(id=stream.id)
        self.assertFalse(stream.is_live)

        stop_response = prepare_stop_stream_response(stop_result)
        stop_response_dict = json.loads(stop_response)
        self.assertEqual(stream.id, stop_response_dict['stream']['id'])
        self.assertEqual(stream.name, stop_response_dict['stream']['name'])
        self.assertEqual(datetime.strftime(stream.start_date, DATE_FORMAT),
                         stop_response_dict['stream']['start_date'])
        self.assertEqual(datetime.strftime(stream.stop_date, DATE_FORMAT),
                         stop_response_dict['stream']['stop_date'])