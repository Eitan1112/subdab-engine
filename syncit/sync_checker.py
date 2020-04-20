import speech_recognition as sr
import re
import random
import numpy as np
import multiprocessing as mp
import string
from difflib import SequenceMatcher
from syncit.constants import Constants
from syncit.subtitle_parser import SubtitleParser
from syncit.helpers import clean_text
import logging
from logger_setup import setup_logging
from syncit.converter import Converter

setup_logging()
logger = logging.getLogger(__name__)


class SyncChecker():
    """
    Class to check if a subtitle file is synced with a video file.

    Attributes:
        data (list): List of lists conatining [base64_buffer, subtitles] e.g: [[f3b5AAA, 'I went to eat'], [a93KKpr, 'I went to sleep']]
    """

    def __init__(self, extension: str, data: list):
        """
        Constructor of the Checker class.

        Params:
            extension (str): The extension of the file.
            data (list): List of lists conatining [base64_buffer, subtitles] e.g: [[f3b5AAA, 'I went to eat'], [a93KKpr, 'I went to sleep']]
        """

        self.data = data
        self.extension = extension

    def check_is_synced(self):
        """
        Checks multiple timepans of the subtitles and compares them to the audio transcript.

        Returns:
            Boolean: Whether the subtitles are in sync with the audio or not.
        """

        similars = 0
        unsimilars = 0

        # Minimun amount of positives needed to declare the subtitles synced
        min_similars = Constants.SAMPLES_TO_CHECK * Constants.SAMPLES_TO_PASS

        with mp.Pool() as pool:
            results = pool.imap_unordered(
                self.check_single_transcript, self.data)

            for result in results:
                if(result == True):
                    similars += 1
                else:
                    unsimilars += 1

                is_synced = similars >= min_similars

                # When the subtitles are synced for sure
                if(is_synced == True):
                    break

                # When the subtitles are unsynced for sure
                if(Constants.SAMPLES_TO_CHECK - min_similars < unsimilars):
                    break

            pool.terminate()

        logger.info(f'Is Synced Result: {is_synced}')
        return is_synced

    def check_single_transcript(self, args: tuple):
        """
        Checks the similarity ratio between subtitles and the video during a certain timespan based on base64 string of the video.

        Params:
            args (tuple): (base64str, subtitles)
                base64str (base64): The base64 buffer of the file.
                subtitles (str): The subtitles of this video.

        Returns:
            Boolean: Whether the video and subtitles are synced or not.
        """

        (base64str, subtitles) = args
        clean_subtitles = clean_text(subtitles)

        # Get Transcritpt
        converter = Converter(base64str, self.extension)
        transcript = converter.convert_video_to_text()
        converter.clean()
        clean_transcript = clean_text(transcript)

        similarity_rate = SequenceMatcher(
            None, clean_transcript, clean_subtitles).ratio()

        logger.debug(
            f"""Subtitles: {subtitles} | Clean Subtitles: {clean_subtitles} | Transcript: {clean_transcript} | Clean Transcript: {clean_transcript} | Similarity: {similarity_rate}""")

        if(similarity_rate > Constants.MIN_ACCURACY):
            return True
        return False
