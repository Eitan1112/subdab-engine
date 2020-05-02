from syncit.constants import Constants
import multiprocessing as mp
import numpy as np
from moviepy.editor import VideoFileClip
from itertools import repeat
import logging
from logger_setup import setup_logging
from syncit.helpers import clean_text
from syncit.subtitle_parser import SubtitleParser
from syncit.converter import Converter
from difflib import SequenceMatcher

setup_logging()
logger = logging.getLogger(__name__)


class DelayChecker():
    """
    Class to check the delay of subtitles and video file.

    Attributes:
        converter (Converter): Converter with the base64 of the timestamp loaded.
        start (float): Start time of the video, compared to the larger video.
        end (float): End time of the video,compared to the larger video.
        sp (SubtitleParser): SubtitleParser object with the subtitles loaded.
        hot_words (tuple): Hot words of this section.
        audio_path (str): Path to audio file of this section
        delays_checked (list): The delays already started checking / checked and are false.
    """

    def __init__(self, base64str: str, timestamp, subtitles: str, extension: str):
        """
        Class to check the delay.

        Params:
            base64str (str): Base64 string of the video to check.
            timestamp (dict): Dictionary containing 'start' and 'end' attributes.
            subtitles (str): The subtitles string.
            extension (str): The extension.
        """

        self.converter = Converter(base64str, extension)
        self.start = timestamp['start']
        self.end = timestamp['end']
        self.sp = SubtitleParser(subtitles)
        self.delays_checked = []

    def check_delay_in_timespan(self):
        """
        Tries to find the delay in the timespan of the class.

        Returns:
            int: Subtitles delay in seconds. 
        """

        # Get valid hot words in timespan (reducing from the end and appending to the start the delay radius to avoid exceeding beyond the file length)
        self.hot_words = self.sp.get_valid_hot_words(self.start, self.end)

        self.audio_path = self.converter.convert_video_to_audio()

        delay = None

        with mp.Pool() as pool:
            results = pool.imap_unordered(
                self.parse_single_hot_word, self.hot_words)
            for result in results:
                if(result):
                    delay = result
                    pool.terminate()
                    break
            pool.close()
            pool.join()

        if(delay):
            logger.info(f"Found delay: {delay}")
            self.converter.clean()
            return delay
        else:
            logger.error(
                f'Unable to find subtitles delay in {self.start}-{self.end}.')
            self.converter.clean()
            return

    def parse_single_hot_word(self, args: tuple):
        """
        Gets a word and a timestamp, and tries to find the delay based on that.
        Tries to find the word time, and if found verifies that the delay is actually correct.

        Params:
            args (tuple) containing:
                hot_word (str): hot word to check.
                subtitles (str): subtitles to verify.
                start (int): start time in seconds of the subtitles.
                end (int): end time in seconds of the subtitles.

        Returns:
            int: The delay. (None if couldn't find)
        """

        (hot_word, subtitles, start, end) = args

        # Calculate time inside audio file
        subtitles_start = start % Constants.DELAY_CHECKER_SECTIONS_TIME
        subtitles_end = end % Constants.DELAY_CHECKER_SECTIONS_TIME

        # The extended radius to check for the hot word
        transcript_start = subtitles_start - Constants.DELAY_RADIUS
        transcript_end = subtitles_end + Constants.DELAY_RADIUS

        # Avoid negative start time
        if (transcript_start < 0):
            transcript_start = 0

        # Gets number of times the hot word is in the audio transcript of the radius time
        hot_word_in_transcript = self.word_in_timespan_occurrences(hot_word, transcript_start, transcript_end)

        # If the hot word is one time in the audio transcript, check when is it said. Else, return None
        if(hot_word_in_transcript == 0):
            logger.debug(f"Word '{hot_word}' is not in timespan.")
            return

        logger.debug(
            f"Word '{hot_word}' is in timespan. Checking the time...")

        # Gets the word start time
        new_subtitles_start = self.get_word_time(hot_word, transcript_start, transcript_end, subtitles_start)

        # If the get_word_time function couldn't find when the word is said, return None
        if(new_subtitles_start is None):
            logger.debug(
                f"Continuing - unable to find the hot word '{hot_word}' in the transcript.")
            return

        # Only got here if we have the time the hot word is said.
        # Calculate the delay
        delay = new_subtitles_start - subtitles_start
        return delay

    def verify_delay(self, delay: float):
        """
        Checks if the delay is correct.

        Params:
            delay (float): The delay.

        Returns:
            bool: Whether the delay is correct or not.
        """

        similars = 0
        unsimilars = 0
        self.delays_checked.append(delay)

        for hot_word_args in self.hot_words:
            (hot_word, subtitles, subtitles_start, subtitles_end) = hot_word_args

            transcript_start = subtitles_start + delay
            transcript_end = subtitles_start + delay + Constants.ONE_WORD_AUDIO_TIME

            occurences = self.word_in_timespan_occurrences(
                hot_word, transcript_start, transcript_end)

            if(occurences > 0):
                logger.debug(
                    f"Hot word '{hot_word}' added to similars in delay {delay}")
                similars += 1
            else:
                logger.debug(
                    f"Hot word '{hot_word}' added to unsimilars in delay {delay}")
                unsimilars += 1

            if(similars > Constants.VERIFY_DELAY_SAMPLES_TO_PASS):
                return True

            if(unsimilars >= Constants.VERIFY_DELAY_SAMPLES_TO_CHECK - Constants.VERIFY_DELAY_SAMPLES_TO_PASS):
                return False

    def get_word_time(self, word: str, start: float, end: float, subtitles_start: float):
        """
        Recursive function that gets a timestamp (with radius initially) and a word, and checks when that word is said in this timestamp.

        Params:
            word (str): Word to check.
            start (float): Start time in seconds.
            end (float): End time in seconds.
            step (float): What is the step in the for loop.
            subtitles_start (float): The start time of the hot word in the subtitles (without the radius)

        Returns:
            float: Start time in seconds the word is said.
        """

        # Calculate step
        step = (end - start) / Constants.DELAY_CHECK_DIVIDER

        # If the section is small, start trimming
        if(end - start <= Constants.SWITCH_TO_TRIMMING_ALGO_TIME):
            logger.debug(
                f"Trimming small section. Word: '{word}'. Start: {start}. End: {end}")
            return self.trim_small_section(word, start, end)

        # Loop through the sections
        for current_start in np.arange(start, end, step):
            current_end = current_start + step + Constants.ONE_WORD_AUDIO_TIME

            # Get occurences of word in section
            current_occurences = self.word_in_timespan_occurrences(
                word, current_start, current_end)
            logger.debug(
                f"Looping. Start: {start}. End: {end}. Step: {step}. current start: {current_start}. Current end: {current_end}. Word: '{word}' Occurences: {current_occurences}.")

            # If word not in section -> abort
            if(current_occurences == 0):
                logger.debug(
                    f"Word: '{word}' is not in this section. Start: {current_start}. End: {current_end}")
                continue

            logger.debug(
                f"Word is at least 1 time in the section. Word: '{word}'. Start: {current_start}. End: {current_end}")
            time = self.get_word_time(
                word, current_start, current_end, subtitles_start)

            # If couldn't find time -> Abort
            if(time is None):
                continue

            # Calculate the delay
            delay = time - subtitles_start

            is_already_checked = any(abs(
                delay - checked_delay) <= Constants.CHECKED_DELAY_RADIUS for checked_delay in self.delays_checked)
            logger.debug(
                f"Verifing sync. Word: '{word}'. Delay: {delay}. Delays_Checked: {self.delays_checked}")
            # If already checked delay -> Abort
            if(is_already_checked):
                logger.debug(
                    f"Delay {delay} of word '{word}' is already checked.'")
                continue

            # Verify delay
            is_delay_verified = self.verify_delay(delay)
            if(is_delay_verified):
                logger.debug(f"Found delay: {delay}. Word: '{word}'.")
                return time
            else:
                logger.debug(
                    f"Word '{word}' with delay {delay} not accuracte enough")

    def trim_small_section(self, word: str, start: float, end: float, step=Constants.TRIM_SECTION_STEP):
        """ 
        Trims a small section by a small step in order to find out the precise start time.
        Suitable for small sections ( < 4s)

        Params:
            word (str): The word to look for in each trim.
            start (float): Start time.
            end (float): End time.
            step (float): The step to trim.

        Returns:
            float: The time after trimming the beginning.
        """

        logger.debug(f"Word '{word}' started trimming. Start: {start}. End: {end}. Step: {step}.")
        for current_start in np.arange(start, end, step):
            occurences = self.word_in_timespan_occurrences(
                word, current_start, end)

            # Continue until trimmed too much
            if(occurences != 0):
                continue

            # If trimmed too much but the step is too large -> start with smaller step
            if(step > Constants.TRIM_SECTION_FINAL_STEP):
                return self.trim_small_section(word, current_start - step,
                                               end, step / Constants.TRIM_SECTION_STEP_DIVIDER)
            # Calculate the final word time
            word_start = current_start - step
            
            # Make sure that the word is actually said by checking a small section
            occurences = self.word_in_timespan_occurrences(
                word, word_start, word_start + Constants.ONE_WORD_AUDIO_TIME)

            if(occurences != 0):
                logger.debug(f"Word '{word}' found time! Time: {word_start}")
                return word_start
            else:
                logger.debug(f"Word '{word}' was false positive and detected.")
                return None

    def check_single_transcript(self, subtitles: str, start: float, end: float):
        """
        Checks the similarity ratio between subtitles and the video during a certain timespan based on the video path.

        Params:
            subtitles (str): The subtitles of this timestamps.
            start (float): Start time of the timestamps in the audio
            end (float): End time of the timestamps in the audio

        Returns:
            Boolean: Whether the video and subtitles are synced or not.
        """

        transcript = self.converter.convert_video_to_text(start, end)
        clean_transcript = clean_text(transcript)

        similarity_rate = SequenceMatcher(
            None, clean_transcript, subtitles).ratio()

        logger.debug(
            f"""Subtitles: {subtitles} | Hot Word: {subtitles.split()[0]} | Clean Subtitles: {subtitles} | Transcript: {clean_transcript} | Clean Transcript: {clean_transcript} | Similarity: {similarity_rate}. Start: {start}. End: {end}""")

        if(similarity_rate > Constants.MIN_ACCURACY):
            return True
        return False

    def word_in_timespan_occurrences(self, word: str, start: float, end: float):
        """
        Checks occurrences of a word in an audio timestamp.

        Params:
            word (str): The word.
            start (float): Start time.
            end (float): End time.

        Returns:
            int: Number of occurrences of word in transcript.
        """

        transcript = self.converter.convert_video_to_text(
            start, end, word)

        count = len(transcript.split())
        logger.debug(
            f"Checked occurrences of '{word}' in {start}-{end}. It is {count} times.")
        return count
