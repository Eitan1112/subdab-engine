import base64
import unittest
import os
from syncit.converter import Converter
from syncit.constants import TestConstants
from werkzeug.datastructures import FileStorage


class TestConverter(unittest.TestCase):
    """
    Class to test the Converter class.
    """

    def setUp(self):
        """
        Setup to run before each test.
        """

        data = open(TestConstants.SAMPLE_VIDEO_PATH, 'rb')
        self.converter = Converter(FileStorage(data), 'mp4')

    def test_convert_video_to_audio(self):
        """
        Tests convert_to_wav method.
        Checks if the conversion is succesful by comparing the size of
        the audio file with the size it supposed to be.
        """

        # Convert the entire file
        audio_path = self.converter.convert_video_to_audio()
        audio_size = os.path.getsize(audio_path)
        self.assertEqual(audio_size, TestConstants.SAMPLE_AUDIO_SIZE)

    def test_convert_audio_to_text(self):
        """
        Test for the convert_audio_to_text method.
        """

        audio_path = TestConstants.SAMPLE_AUDIO_PATH
        desired_transscripts = TestConstants.TRANSCRIPT_FROM_SPHINX
        start = TestConstants.TRANSCRIPT_TIMESTAMP_START
        end = TestConstants.TRANSCRIPT_TIMESTAMP_END

        recieved_transcript = self.converter.convert_audio_to_text(
            audio_path, start, end)

        self.assertTrue((recieved_transcript in desired_transscripts))

    def test_convert_media_to_text(self, audio_path=None):
        """
        Test for both the convert_video_to_text method and convert_audio_to_text methods.
        """

        desired_transscripts = TestConstants.TRANSCRIPT_FROM_SPHINX
        start = TestConstants.TRANSCRIPT_TIMESTAMP_START
        end = TestConstants.TRANSCRIPT_TIMESTAMP_END

        recieved_transcript = self.converter.convert_video_to_text(
            start, end)

        self.assertTrue((recieved_transcript in desired_transscripts))

    def tearDown(self):
        """
        Teardown to run after each test - cleans.
        """

        self.converter.clean()
