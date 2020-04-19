import unittest
import os
from syncit.converter import Converter
from syncit.constants import TestConstants

class TestConverter(unittest.TestCase):
    """
    Class to test the Converter class.
    """

    def setUp(self):
        """
        Setup to run before each test.
        """

        self.converter = Converter(TestConstants.SAMPLE_VIDEO_PATH)

    
    def test_convert_video_to_audio(self):
        """
        Tests convert_to_wav method.
        Checks if the conversion is succesful by comparing the size of
        the audio file with the size it supposed to be.
        """

        # Convert the entire file
        audio_path = self.converter.convert_video_to_audio(-1000.5, 1000.5)
        
        audio_size = os.path.getsize(audio_path)
        self.assertEqual(audio_size, TestConstants.SAMPLE_AUDIO_SIZE)



    def test_convert_audio_to_text(self):
        """
        Test for the convert_audio_to_text method.
        """

        audio_path = TestConstants.SAMPLE_AUDIO_PATH
        self.test_convert_media_to_text(audio_path)

    
    def test_convert_media_to_text(self, audio_path=None):
        """
        Test for both the convert_video_to_text method and convert_audio_to_text methods.
        """

        desired_transscripts = TestConstants.TRANSCRIPT_FROM_SPHINX
        start = TestConstants.TRANSCRIPT_TIMESTAMP_START
        end = TestConstants.TRANSCRIPT_TIMESTAMP_END

        if(audio_path):
            recieved_transcript = self.converter.convert_audio_to_text(audio_path, start, end)
        else:
            recieved_transcript = self.converter.convert_video_to_text(start, end)

        is_good = recieved_transcript in desired_transscripts
        self.assertTrue(is_good)

        hot_word = TestConstants.SAMPLE_WORD
        (start, end) = TestConstants.SAMPLE_WORD_TIMESTAMP

        if(audio_path):
            recieved_transcript = self.converter.convert_audio_to_text(audio_path, start, end, hot_word)
        else:
            recieved_transcript = self.converter.convert_video_to_text(start, end, hot_word)
        self.assertEqual(recieved_transcript.strip(), hot_word.strip())

    


    def tearDown(self):
        """
        Teardown to run after each test - cleans.
        """

        self.converter.clean()