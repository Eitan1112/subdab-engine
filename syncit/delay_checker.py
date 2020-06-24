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
        logger.debug(f'Hot words: {self.hot_words} start: {start} end: {end}')
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
                ids (list): list of ids of words in the section.
                start (float): Start time.
                end (float): End time.
        """
        
        sections_items = []
        for section_start in range(self.start, self.end, Constants.DIVIDED_SECTIONS_TIME):
            section_end = section_start + Constants.DIVIDED_SECTIONS_TIME + Constants.ONE_WORD_AUDIO_TIME 
            if(section_end > self.end): section_end = self.end # Handle edge case where the end time is after the audio end time
            section_item = {'ids': [], 'start': section_start, 'end': section_end}

            # Append ids of hot words inside timespan
            for hot_word_item in self.hot_words:
                hot_word_start = hot_word_item['start'] - Constants.DELAY_RADIUS
                hot_word_end = hot_word_item['end'] + Constants.DELAY_RADIUS
                is_word_in_section = hot_word_start < section_end and hot_word_end > section_start
                if(is_word_in_section):
                    section_item['ids'].append(hot_word_item['ids'])

            sections_items.append(section_item)

        # Remove Empty Sections
        sections_items = [section_item for section_item in sections_items if len(section_item['ids']) > 0]
        logger.debug(f'Sections_items {sections_items}')
        return sections_items