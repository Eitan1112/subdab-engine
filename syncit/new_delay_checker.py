import multiprocessing as mp
from multiprocessing import shared_memory
import numpy as np
import random
from moviepy.editor import VideoFileClip
from itertools import repeat
from difflib import SequenceMatcher
import uuid
import logging
from syncit.constants import Constants
from logger_setup import setup_logging
from syncit.helpers import clean_text
from syncit.subtitle_parser import SubtitleParser
from syncit.converter import Converter

setup_logging()
logger = logging.getLogger(__name__)


class DelayChecker():
    """
    Class to check the delay of subtitles and video file.

    Attributes:
        converter (Converter): Converter with the video file of the timestamp loaded.
        start (float): Start time of the video, compared to the larger video.
        end (float): End time of the video,compared to the larger video.
        sp (SubtitleParser): SubtitleParser object with the subtitles loaded.
        hot_words (tuple): Hot words of this section.
        self.falty_delays (list): list of delays already verified falty. 
    """

    def __init__(self, audio_file, start: int, end: int, subtitles_file: str, audio_language: str, subtitles_language: str):
        """
        Class to check the delay.

        Params:
            audio_file (FileStorage): Object with the video file loaded.
            start (int): Start time of the video.
            end (int): End time of the video.
            subtitles_file (FileStorafe): The subtitles file.
            extension (str): The extension.
        """

        self.converter = Converter(audio_file, audio_language)
        self.start = start
        self.end = end
        self.sp = SubtitleParser(subtitles_file, subtitles_language)
        self.audio_language = audio_language
        self.subtitles_language = subtitles_language
        self.hot_words = self.sp.get_valid_hot_words(start, end, audio_language)
        self.falty_delays = []

    def check_delay(self):
        """
        Check the delay.

        Returns:
            float: The delay.
        """


    def get_grouped_sections(self):
        """
        Divides the audio file to sections and gets the hot words to check for.

        Returns:
            list of dicts:
                ids (str): ids of word.
                start (float): Start time.
                end (float): End time.
        """

        