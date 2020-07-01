import base64
import unittest
import os
from moviepy.editor import AudioFileClip
from syncit.converter import Converter
from syncit.constants import Constants
from werkzeug.datastructures import FileStorage

# Setup Constants
SAMPLE_AUDIO = os.path.join(Constants.SAMPLES_FOLDER, 'audio.m4a')
LANGUAGE = 'en'

# test_language_conversion Constants
LANGUAGE_CODE = 'en-US'

# test_convert_audio_to_text Constants
WORD = 'elsa'
START = 57
END = 60


class TestConverter(unittest.TestCase):
    """
    Class to test the Converter class.
    """

    def setUp(self):
        """
        Setup to run before each test.
        """

        audio = open(SAMPLE_AUDIO, 'rb')
        self.converter = Converter(FileStorage(audio), 'en')
        audio.close()

    def test_language_conversion(self):
        """
        Make sure the language is correct.
        """

        self.assertEqual(self.converter.language, LANGUAGE_CODE,
                         'Check the language conversion.')

    def test_repair_file(self):
        """
        Make sure the output file is wav format that can be used in moviepy.
        """

        audio_path = self.converter.audio
        self.assertTrue(audio_path.endswith('.wav'))
        # Make sure it can be loaded in moviepy
        clip = AudioFileClip(audio_path)

    def test_convert_audio_to_text(self):
        """
        Check the convert_audio_to_text method.
        """

        text = self.converter.convert_audio_to_text(START, END, [WORD], lambda: False)
        text = text.strip()
        self.assertEqual(text, WORD)
