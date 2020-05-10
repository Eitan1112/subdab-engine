import unittest
import os
import tempfile
from werkzeug.datastructures import FileStorage
from syncit.subtitle_parser import SubtitleParser
from syncit.constants import TestConstants

DIRNAME = os.path.dirname(os.path.abspath(__name__))

# Setup Constant
SAMPLE_SUBTITLES_PATH = os.path.join(
    DIRNAME, 'syncit', 'tests', 'samples', 'subtitles.srt')
SAMPLE_SUBTITLES_LANGUAGE = 'en'

# test_read_subtitles Constants
SAMPLE_SUBTITLES_STRING_LENGTH = 202842
SAMPLE_SUBTITLES_GROUPS_AMOUNT = 1894

# test_get_subtitles Constants
INDEX = 1885
INDEX_SUBTITLES = 'and then a bunch of important things happen that i forgot'

# test_get_valid_hot_words Constants
START = 0
END = 75
WORDS = (('bedtime', 'bedtime soon', 67.4, 68.37),
         ('uhoh', 'uhoh the princess is trapped', 68.373, 70.239),
         ('quick', 'quick elsa make a prince a fancy one', 71.811, 74.611))
LANGUAGE = 'en'

# test_check_word_occurences_in_timespan Constants
OCCURENCES_START = 60
OCCURENCES_END = 90
OCCURENCES_WORD = 'anna'
OCCURENCES = 2


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

    def test_check_word_occurences_in_timespan(self):
        """
        Make sure return correct amount of occurences of word in timestamp.
        """

        occurences = self.sp.check_word_occurences_in_timespan(
            OCCURENCES_WORD, OCCURENCES_START, OCCURENCES_END)

        self.assertEqual(occurences, OCCURENCES, 'Check check_word_occurences_in_timespan.')
        