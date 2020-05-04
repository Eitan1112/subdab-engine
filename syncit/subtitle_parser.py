import re
import random
from syncit.constants import Constants
from syncit.helpers import convert_subs_time, clean_text
import logging
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


class SubtitleParser():
    """
    Read the subtitles and parses them for ease of use.

    Attributes:
        subtitles (str): Subtitles file content.
        re_subs (list): List of tuples containing the parsed subtitles.
    """

    def __init__(self, subtitles: str):
        """
        Constructor for the SubtitlesParser class.

        Params:
            subtitles (str): Subtitles string. 
        """

        self.subtitles = subtitles
        self.read_subtitles()

    def read_subtitles(self):
        """
        Reads the subtitle content using regex and stores it in memory for easy access.
        """

        # Group 1: index, Group 2: Start Time, Group 3: End Time, Group 4: Text
        pattern = r"(\d+)\r\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\r\n((?:.+\r\n)*.+)"

        re_subs = re.findall(pattern, self.subtitles, re.M | re.I)

        self.re_subs = re_subs

    def get_subtitles(self, index: int):
        """
        Gets cleaned subtitles and the timespan of a specific index in seconds.

        Params:
            index (int): Index

        Returns:
            tuple: (cleaned_subtitles, start, end)
        """

        match = self.re_subs[index - 1]
        start = convert_subs_time(match[1])
        end = convert_subs_time(match[2])
        subtitles = match[3]
        subtitles = clean_text(subtitles)

        return (subtitles, start, end)

    def get_valid_hot_words(self, start: float, end: float):
        """
        Loops through the subtitles and finds valid hot words in the specified timespan.

        Params:
            start (float): start time.
            end (float): end time.

        Returns:
            tuple: A tuple of tuples containing: (hot word, subtitles, start, end).
        """

        valid_hot_words = []

        subs_length = len(self.re_subs)

        for sub in range(1, subs_length):

            # Get the subtitles by index
            (subtitles, subtitles_start, subtitles_end) = self.get_subtitles(sub)

            # Skip to the start time
            if(subtitles_start < start):
                continue

            # Reached the end
            if(subtitles_end > end):
                break

            # Don't check empty subtitles (e.g.: {Quack})
            try:
                hot_word = subtitles.split()[0]
            except:
                continue
            
            # Don't check popular hot words, waste of time
            if(hot_word in Constants.COMMON_WORDS_UNSUITABLE_FOR_DETECTION):
                continue
                
            # Don't take numbers as hot words
            if(hot_word.replace('.', '', 1).isdigit()): # The replace is if the number is a float
                continue

            # Make sure the word is only one time in the radius
            word_occurences_in_timespan = self.check_word_occurences_in_timespan(
                hot_word, subtitles_start - Constants.DELAY_RADIUS, subtitles_start + Constants.DELAY_RADIUS)
            
            if(word_occurences_in_timespan > 1):
                continue

            valid_hot_words.append(
                (hot_word, subtitles, subtitles_start, subtitles_end))

        return tuple(valid_hot_words)

    def check_word_occurences_in_timespan(self, word: str, start: float, end: float):
        """
        Checks the number of occurences of a word in a timespan.

        Params:
            word (str): The word to look for.
            start (float): The start time.
            end (float): End time.

        Returns:
            int: Occurences of the word in the timespan.
        """

        subs_length = len(self.re_subs)
        occurences = 0

        for sub in range(1, subs_length):

            # Get the subtitles by index
            (subtitles, subtitles_start, subtitles_end) = self.get_subtitles(sub)

            # Skip to the start time
            if(subtitles_start < start):
                continue

            # Reached the end
            if(subtitles_end > end):
                break

            # Add the amount of times the word is said
            occurences += subtitles.split().count(word)

        return occurences
