import base64
import unittest
import os
from moviepy.editor import AudioFileClip
from syncit.delay_checker import DelayChecker
from syncit.constants import Constants
from werkzeug.datastructures import FileStorage

### Constants ###
SAMPLE_AUDIO_PATH = os.path.join(Constants.SAMPLES_FOLDER, 'audio.m4a')
SAMPLE_SUBTITLES_PATH = os.path.join(Constants.SAMPLES_FOLDER, 'subtitles.srt')
START = 0
END = 80
AUDIO_LANGUAGE = 'en'
SUBTITLES_LANGUAGE = 'en'

class TestDelayChecker(unittest.TestCase):
    """
    Class to test the DelayChecker class.
    """

    def setUp(self):
        """
        Creates a DelayChecker instance.
        """
        
        sample_subtitles_file = open(SAMPLE_SUBTITLES_PATH, 'rb')
        sample_audio_file = open(SAMPLE_AUDIO_PATH, 'rb')
        self.dc = DelayChecker(FileStorage(sample_audio_file), START, END, FileStorage(sample_subtitles_file), AUDIO_LANGUAGE, SUBTITLES_LANGUAGE)
        sample_subtitles_file.close()
        sample_audio_file.close()
    
    # def test_get_grouped_sections(self):
    #     """
    #     Test the get_grouped_sections method.
    #     """

    #     grouped_sections = self.dc.get_grouped_sections()


    def test_get_occurences_for_grouped_sections(self):
        self.dc.check_delay()