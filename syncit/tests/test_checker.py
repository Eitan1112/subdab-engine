import unittest
from syncit.checker import Checker
from syncit.constants import TestConstants


class TestChecker(unittest.TestCase):
    """
    Class for testing the checker class.

    Attributes:
        synced_checker (Checker object): Checker object with synced subtitles
        early_checker (Checker object): Checker object with early subtitles
        late_checker (Checker object): Checker object with late subtitles
    """

    def setUp(self):
        """
        setUp method that creates a checker object before each test.
        """

        video = TestConstants.SAMPLE_VIDEO_PATH

        synced = TestConstants.SAMPLE_SYNCED_PATH
        early = TestConstants.SAMPLE_EARLY_PATH
        late = TestConstants.SAMPLE_LATE_PATH

        self.synced_checker = Checker(video, synced)
        self.early_checker = Checker(video, early)
        self.late_checker = Checker(video, late)

    
    def test_check_single_transcript_by_index(self):
        """
        Test for the method check_single_trancript.
        """

        is_synced = self.synced_checker.check_single_transcript_by_index(TestConstants.SUBTITLES_INDEX_FOR_TRANSCRIPT)
        self.assertTrue(is_synced)

        is_synced = self.early_checker.check_single_transcript_by_index(TestConstants.SUBTITLES_INDEX_FOR_TRANSCRIPT)
        self.assertFalse(is_synced)

        is_synced = self.late_checker.check_single_transcript_by_index(TestConstants.SUBTITLES_INDEX_FOR_TRANSCRIPT)
        self.assertFalse(is_synced)


    def test_check_is_synced(self):
        """
        Test for the method check_timespan.
        """
        
        synced_checker = Checker(TestConstants.LONG_SAMPLE_VIDEO, TestConstants.LONG_SAMPLE_SYNCED)
        unsynced_checker = Checker(TestConstants.LONG_SAMPLE_VIDEO, TestConstants.LONG_SAMPLE_UNSYNCED)

        synced_result = synced_checker.check_is_synced()
        self.assertTrue(synced_result, 'Synced subtitles marked as unsynced.')

        unsynced_result = unsynced_checker.check_is_synced()
        self.assertFalse(unsynced_result, 'Unsynced subtitles marked as synced.')


    def test_check_single_transcript(self):
        """
        Test for the check_single_transcript method.
        """

        subtitles = TestConstants.TRANSCRIPT_IN_TIMESTAMP
        not_subtitles = TestConstants.NOT_TRANSCRIPT_IN_TIMESTAMP
        start = TestConstants.TRANSCRIPT_TIMESTAMP_START
        end = TestConstants.TRANSCRIPT_TIMESTAMP_END

        synced_result = self.synced_checker.check_single_transcript(subtitles, start, end)
        self.assertTrue(synced_result)

        unsynced_result = self.synced_checker.check_single_transcript(not_subtitles, start, end)
        self.assertFalse(unsynced_result)


if __name__ == '__main__':
    unittest.main()
