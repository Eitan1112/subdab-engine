import unittest
from syncit.constants import TestConstants
from syncit.delay_checker import DelayChecker

class TestDelayChecker(unittest.TestCase):
    """
    Class to test DelayChecker class.

    Attributes:
        dc (DelayChecker): delay checker object with unsynced subtitles.
    """

    def setUp(self):
        """
        Creates a DelayChecker object with the sample video and the synced subtitles.
        """

        self.dc = DelayChecker(TestConstants.SAMPLE_VIDEO_PATH, TestConstants.SAMPLE_SYNCED_PATH)
        self.audio_path = TestConstants.SAMPLE_AUDIO_PATH
        self.word = TestConstants.SAMPLE_WORD
        (self.start, self.end) = TestConstants.SAMPLE_WORD_TIMESTAMP
        self.step = TestConstants.INITIAL_DELAY_CHECK_STEP


    def test_get_word_time(self):
        """
        Test for the method get_word_time.
        """
        
        audio_path = TestConstants.SAMPLE_AUDIO_PATH
        word = TestConstants.SAMPLE_WORD
        real_word_time = TestConstants.SAMPLE_WORD_TIME
        (start, end) = TestConstants.SAMPLE_WORD_TIMESTAMP
        step = TestConstants.INITIAL_DELAY_CHECK_STEP

        recieved_word_time = self.dc.get_word_time(audio_path, word, start, end, step)
        self.assertIsNotNone(recieved_word_time, 'Unable to find the word time')
        self.assertLess(recieved_word_time, real_word_time + 1)
        self.assertGreater(recieved_word_time, real_word_time - 1)

    def test_get_word_results_in_section(self):
        """
        Test for the get_word_results_in_section method.
        """
        (sections_occurences, sections_timestamps) = self.dc.get_word_results_in_section(self.audio_path, self.word, self.start, self.end, self.step)

        sections_occurences = TestConstants.SAMPLE_WORD_SECTIONS_OCCURENCES
        sections_timestamps = TestConstants.SAMPLE_WORD_SECTIONS_TIMESTAMPS
        self.assertEqual(sections_occurences, sections_occurences)
        self.assertEqual(sections_timestamps, sections_timestamps)


    def test_word_in_timespan_occurrences(self):
        """
        Test for the word_in_timespan_occurrences method.
        """

        one_occurence = self.dc.word_in_timespan_occurrences(self.audio_path, self.word, self.start, self.end)
        zero_occurences = self.dc.word_in_timespan_occurrences(self.audio_path, 'gibrishword', self.start, self.end)
        self.assertEqual(one_occurence, 1)
        self.assertEqual(zero_occurences, 0)


    def test_parse_single_hot_word(self):
        """
        Test for the parse_single_hot_word method.
        """

        unsynced_dc = DelayChecker(TestConstants.LONG_SAMPLE_VIDEO, TestConstants.LONG_SAMPLE_UNSYNCED)
        audio_path = TestConstants.LONG_SAMPLE_AUDIO
        transcript = TestConstants.LONG_SAMPLE_WORD_TRANSCRIPT
        word = TestConstants.LONG_SAMPLE_WORD
        (start, end) = TestConstants.LONG_SAMPLE_WORD_TIMESTAMP
        args = (audio_path, word, transcript, start, end)
        delay = unsynced_dc.parse_single_hot_word(args)
        desired_delay = TestConstants.LONG_SAMPLE_DELAY
        self.assertGreater(delay, desired_delay - 0.5)
        self.assertLess(delay, desired_delay + 0.5)
        unsynced_dc.converter.clean()

    def test_check_delay_in_timespan(self):
        """
        Test for the check_delay_in_timespan method.
        """

        unsynced_dc = DelayChecker(TestConstants.LONG_SAMPLE_VIDEO, TestConstants.LONG_SAMPLE_UNSYNCED)
        audio_path = TestConstants.LONG_SAMPLE_AUDIO
        delay = unsynced_dc.check_delay_in_timespan(audio_path, 0, TestConstants.DELAY_CHECKER_SECTIONS_TIME)
        desired_delay = TestConstants.LONG_SAMPLE_DELAY
        self.assertGreater(delay, desired_delay - 0.5)
        self.assertLess(delay, desired_delay + 0.5)
        unsynced_dc.converter.clean()

    def test_check_delay(self):
        """
        Test for the check_delay method.
        """
        
        unsynced_dc = DelayChecker(TestConstants.LONG_SAMPLE_VIDEO, TestConstants.LONG_SAMPLE_UNSYNCED)
        delay = unsynced_dc.check_delay()
        desired_delay = TestConstants.LONG_SAMPLE_DELAY
        self.assertGreater(delay, desired_delay - 0.5)
        self.assertLess(delay, desired_delay + 0.5)
        unsynced_dc.converter.clean()

    def tearDown(self):
        self.dc.converter.clean()


if(__name__ == '__main__'):
    unittest.main()