import unittest
import os
import tempfile
from werkzeug.datastructures import FileStorage
from syncit.constants import Constants
from syncit.subtitle_parser import SubtitleParser

# Setup Constant
SAMPLE_SUBTITLES_PATH = os.path.join(Constants.SAMPLES_FOLDER, 'subtitles.srt')
SAMPLE_SUBTITLES_LANGUAGE = 'en'

# test_read_subtitles Constants
SAMPLE_SUBTITLES_STRING_LENGTH = 202842
SAMPLE_SUBTITLES_GROUPS_AMOUNT = 1894

# test_get_subtitles Constants
INDEX = 1885
INDEX_SUBTITLES = 'and then a bunch of important things happen that i forgot'

# test_get_valid_hot_words Constants
START = 66
END = 75
WORDS = [{'hot_word': 'bedtime', 'subtitles': 'bedtime soon', 'start': 67.4, 'end': 68.37},
         {'hot_word': 'uhoh', 'subtitles': 'uhoh the princess is trapped',
             'start': 68.373, 'end': 70.239},
         {'hot_word': 'in', 'subtitles': 'in the snow goblins evil spell',
             'start': 70.242, 'end': 71.808},
         {'hot_word': 'quick', 'subtitles': 'quick elsa make a prince a fancy one', 'start': 71.811, 'end': 74.611}]
LANGUAGE = 'en'

# test_filter_hot_words Constants
HOT_WORDS = [
    {'hot_word': 'hello', 'subtitles': 'hello this is me something', 'start': 0, 'end': 11},
    {'hot_word': 'take', 'subtitles': 'take it', 'start': 11, 'end': 13},
    {'hot_word': 'something', 'subtitles': 'something like that', 'start': 14, 'end': 15},
    {'hot_word': 'please', 'subtitles': 'please dont take me', 'start': 70, 'end': 80},
]

DESIRED_FILTERED_HOT_WORDS = [
    {'hot_word': 'hello', 'subtitles': 'hello this is me something', 'start': 0, 'end': 11},
    {'hot_word': 'take', 'subtitles': 'take it', 'start': 11, 'end': 13},
    {'hot_word': 'please', 'subtitles': 'please dont take me', 'start': 70, 'end': 80},
]


class TestSubtitleParser(unittest.TestCase):
    """
    Test for SubtitleParser class.

    Attributes:
        sp (SubtitleParser object): SubtitleParser with sample subtitles.
    """

    def setUp(self):
        """
        Create a sp instance.
        """

        subtitles_binary = open(SAMPLE_SUBTITLES_PATH, 'rb')
        subtitles_file = FileStorage(subtitles_binary)
        self.sp = SubtitleParser(subtitles_file, SAMPLE_SUBTITLES_LANGUAGE)
        subtitles_binary.close()

    def test_read_subtitles(self):
        """
        Makes sure the re_subs length is as expected.
        """

        re_subs_length = len(self.sp.re_subs)
        self.assertEqual(re_subs_length, SAMPLE_SUBTITLES_GROUPS_AMOUNT,
                         'Check re_subs length (maybe the regex pattern?).')

    def test_get_subtitles(self):
        """
        Make sure you get the expected subtitles.
        """

        (subtitles, start, end) = self.sp.get_subtitles(INDEX)
        self.assertEqual(subtitles, INDEX_SUBTITLES, 'Check get_subtitles.')

    def test_get_valid_hot_words(self):
        """
        Make sure you get only valid hot words.
        """

        hot_words = self.sp.get_valid_hot_words(START, END, LANGUAGE)
        self.assertEqual(hot_words, WORDS, 'Check get_valid_hot_words.')

    def test_filter_hot_words(self):
        """
        Make sure that filter_hot_words removes the correct subtitles.
        """

        recieved_hot_words = self.sp.filter_hot_words(HOT_WORDS)
        self.assertEqual(recieved_hot_words, DESIRED_FILTERED_HOT_WORDS)
