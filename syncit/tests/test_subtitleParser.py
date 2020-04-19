import unittest
import os
import tempfile
from syncit.subtitle_parser import SubtitleParser
from syncit.constants import TestConstants


class TestSubtitleParser(unittest.TestCase):
    """
    Test for SubtitleParser class.

    Attributes:
        sp (SubtitleParser object): SubtitleParser with the synced subs.
    """

    def setUp(self):
        """
        Creates an sp attribute with the synced subtitles sample.
        """

        self.sp = SubtitleParser(TestConstants.SAMPLE_SYNCED_PATH)

    def test_get_subtitles(self):
        """
        Test for the get_subtitles method.
        """

        (subtitles, start, end) = self.sp.get_subtitles(1)

        desired_subtitles = TestConstants.TRANSCRIPT_IN_TIMESTAMP
        desired_start = TestConstants.TRANSCRIPT_TIMESTAMP_START
        desired_end = TestConstants.TRANSCRIPT_TIMESTAMP_END

        self.assertEqual(subtitles, desired_subtitles)
        self.assertEqual(start, desired_start)
        self.assertEqual(end, desired_end)

        with self.assertRaises(IndexError):
            self.sp.get_subtitles(10000000)

      

    def test_get_valid_indexes(self):
        """
        Test for get_valid_indexes method.
        """

        valid_indexes = SubtitleParser(TestConstants.SUBTITLES_SAMPLE).get_valid_indexes()
        valid_indexes.sort()

        desired_valid_indexes = TestConstants.SAMPLE_SUBTITLES_VALID_INDEXES

        self.assertEqual(valid_indexes, desired_valid_indexes)


    def test_sync_subtitles(self):
        """
        Test for sync_subtitles method.
        """

        synced = TestConstants.SAMPLE_SYNCED_PATH
        early = TestConstants.SAMPLE_EARLY_PATH
        delay = TestConstants.SAMPLE_EARLY_VS_SYNCED_DELAY
        early_sp = SubtitleParser(early)
            
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'early.srt')
            early_sp.sync_subtitles(delay, path)

            with open(path, 'r') as f:
                should_be_synced = f.read()

        with open(synced, 'r') as f:
            definitely_synced = f.read()

        self.assertEqual(should_be_synced, definitely_synced)


    def test_get_valid_hot_words(self):
        """
        Test for get_valid_hot_words method.
        """

        
        sp = SubtitleParser(TestConstants.SUBTITLES_SAMPLE)
        desired_valid_hot_words = TestConstants.SAMPLE_VALID_HOT_WORDS
        start = TestConstants.SAMPLE_HOT_WORDS_START
        end = TestConstants.SAMPLE_HOT_WORDS_END

        recieved_valid_hot_words = sp.get_valid_hot_words(start, end)
        desired_valid_hot_words.sort()
        recieved_valid_hot_words.sort()

        self.assertEqual(desired_valid_hot_words, recieved_valid_hot_words)
