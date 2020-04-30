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

    def check_delay_in_timespan(self):
        """
        Tries to find the delay in the timespan of the class.

        Returns:
            int: Subtitles delay in seconds. 
        """

        # Get valid hot words in timespan (reducing from the end and appending to the start the delay radius to avoid exceeding beyond the file length)
        self.hot_words = self.sp.get_valid_hot_words(self.start, self.end)

        audio_path = self.converter.convert_video_to_audio()

        # Add to the start of each tuple in valid_hot_words the audio_path
        imap_args = [tuple([audio_path] + list(element))
                     for element in self.hot_words]

        delay = None

        with mp.Pool() as pool:
            results = pool.imap_unordered(
                self.parse_single_hot_word, imap_args)
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
                audio_path (str): Path to audio file.
                hot_word (str): hot word to check.
                subtitles (str): subtitles to verify.
                start (int): start time in seconds of the subtitles.
                end (int): end time in seconds of the subtitles.

        Returns:
            int: The delay. (None if couldn't find)
        """

        (audio_path, hot_word, subtitles, start, end) = args

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
        hot_word_in_transcript = self.word_in_timespan_occurrences(
            audio_path, hot_word, transcript_start, transcript_end)

        # If the hot word is one time in the audio transcript, check when is it said. Else, return None
        if(hot_word_in_transcript >= 1):
            logger.debug(
                f"Word '{hot_word}' is in timespan. Checking the time...")

            # Gets the word start time
            new_subtitles_start = self.get_word_time(
                audio_path, hot_word, transcript_start, transcript_end)

            # If the get_word_time function couldn't find when the word is said, return None
            if(new_subtitles_start is None):
                logger.debug(
                    f"Continuing - unable to find the hot word '{hot_word}' in the transcript.")
                return

        else:
            logger.debug(
                f'Continuing - word is {hot_word_in_transcript} times in transcript, instead of 1.')
            return

          # Only got here if we have the time the hot word is said.
        # Calculate the delay
        delay = new_subtitles_start - subtitles_start

        # Verify the sync worked
        logger.debug(
            f"Verifing the sync worked. Word: '{hot_word}'. Delay: {delay}")
        is_delay_verified = self.verify_delay(audio_path, delay)
        if(is_delay_verified):
            logger.debug(f"Found delay: {delay}. Word: '{hot_word}'.")
            return delay
        else:
            logger.debug(
                f"Word {hot_word} with delay {delay} not accuracte enough")

    def verify_delay(self, audio_path: str, delay: float):
        """
        Checks if the delay is correct.

        Params:
            delay (float): The delay.

        Returns:
            bool: Whether the delay is correct or not.
        """

        similars = 0
        unsimilars = 0

        for hot_word_args in self.hot_words:
            (hot_word, subtitles, subtitles_start, subtitles_end) = hot_word_args

            transcript_start = subtitles_start + delay
            transcript_end = subtitles_start + delay + Constants.ONE_WORD_AUDIO_TIME

            occurences = self.word_in_timespan_occurrences(
                audio_path, hot_word, transcript_start, transcript_end)

            if(occurences > 0):
                similars += 1
            else:
                unsimilars += 1

            if(similars + unsimilars == Constants.VERIFY_DELAY_SAMPLES_TO_CHECK):
                break
        

    def get_word_time(self, audio_path: str, word: str, start: float, end: float):
        """
        Recursive function that gets a timestamp (with radius initially) and a word, and checks when that word is said in this timestamp.

        Params:
            audio_path (str): Path to audio file.
            word (str): Word to check.
            start (float): Start time in seconds.
            end (float): End time in seconds.
            step (float): What is the step in the for loop.

        Returns:
            float: Start time in seconds the word is said.
        """

        step = (end - start) / 4
        if(end - start <= Constants.SWITCH_TO_TRIMMING_ALGO_TIME):
            logger.debug(
                f"Trimming small section. Word: '{word}'. Start: {start}. End: {end}")
            return self.trim_small_section(audio_path, word, start, end)

        for current_start in np.arange(start, end, step):
            current_end = current_start + step + Constants.ONE_WORD_AUDIO_TIME
            current_occurences = self.word_in_timespan_occurrences(
                audio_path, word, current_start, current_end)
            logger.debug(
                f"Looping. Start: {start}. End: {end}. Step: {step}. current start: {current_start}. Current end: {current_end}. Word: '{word}' Occurences: {current_occurences}.")
            if(current_occurences > 0):
                logger.debug(
                    f"Word is at least 1 time in the section. Word: '{word}'. Start: {current_start}. End: {current_end}")
                time = self.get_word_time(
                    audio_path, word, current_start, current_end)
                if(time):
                    logger.debug(
                        f"Found word time. Word: '{word}'. Start: {current_start}. End: {current_end}. Time: {time}")
                    return time
            logger.debug(
                f"Unable to find word time. Word: '{word}'. Start: {current_start}. End: {current_end}")

    def trim_small_section(self, audio_path: str, word: str, start: float, end: float):
        """ 
        """
        # TODO add docstring

        step = 0.1  # TODO add to constants

        for current_start in np.arange(start, end, step):
            occurences = self.word_in_timespan_occurrences(
                audio_path, word, current_start, end)
            logger.debug(
                f"Word: '{word}'. Start: {start}. End: {end}. Occurences: {occurences}")
            if(occurences == 0):
                return current_start - step

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

    def word_in_timespan_occurrences(self, audio_path: str, word: str, start: float, end: float):
        """
        Checks occurrences of a word in an audio timestamp.

        Params:
            audio_path (str): Path to audio file.
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
