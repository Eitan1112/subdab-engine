import re
import random
from syncit.constants import Constants
from syncit.helpers import convert_subs_time, clean_text
from google.cloud import translate_v2 as translate
import logging
import os
from chardet import detect as detect_encoding
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

# [1::] Because first character is \u202a
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Constants.GOOGLE_APPLICATION_CREDENTIALS_PATH[1::]
translate_client = translate.Client()


class SubtitleParser():
    """
    Read the subtitles and parses them for ease of use.

    Attributes:
        subtitles (str): Subtitles file content.
        re_subs (list): List of tuples containing the parsed subtitles.
        language (str): Language of the subtitles.
        encoding (str): The encoding of the subtitles.
    """

    def __init__(self, subtitles_file, language: str):
        """
        Constructor for the SubtitlesParser class.

        Params:
            subtitles_file (FileStorage): File with the subtitles loaded.
            language (str): The language of the subtitles.
        """

        subtitles_binary = subtitles_file.read()
        encoding = detect_encoding(subtitles_binary)['encoding']
        self.subtitles = subtitles_binary.decode(encoding)
        self.encoding = encoding
        logger.debug(f'Subtitles Encoding: {encoding}')
        logger.debug(f'Subtitles[:100]: {[self.subtitles[:1000]]}')
        self.read_subtitles()
        self.language = language

    def read_subtitles(self):
        """
        Reads the subtitle content using regex and stores it in memory for easy access.
        """

        # Group 1: index, Group 2: Start Time, Group 3: End Time, Group 4: Text

        pattern = r"(\d+)\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\n((?:.+\n)*.+)"
        re_subs = re.findall(pattern, self.subtitles, re.M | re.I)
        if(len(re_subs) < 1):
            pattern = r"(\d+)\r\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\r\n((?:.+\r\n)*.+)"
            re_subs = re.findall(pattern, self.subtitles, re.M | re.I)
        
        if(len(re_subs) < 1):
            raise Exception(f're_subs length is {len(re_subs)}. Maybe the regex pattern is falty?')

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

    def get_valid_hot_words(self, start: float, end: float, target_language=None):
        """
        Loops through the subtitles and finds valid hot words in the specified timespan.

        Params:
            start (float): start time.
            end (float): end time.
            target_language (str): The language to get the hot words in. If None, the original language.

        Returns:
            tuple: A tuple of tuples containing: (hot word, subtitles, start, end).
        """

        valid_hot_words = []

        subs_length = len(self.re_subs)
        logger.debug(f'Subs Length: {subs_length}')

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
            if(hot_word.replace('.', '', 1).isdigit()):  # The replace is if the number is a float
                continue

            # Make sure the word is only one time in the radius
            word_occurences_in_timespan = self.check_word_occurences_in_timespan(
                hot_word, subtitles_start - Constants.DELAY_RADIUS, subtitles_start + Constants.DELAY_RADIUS)
            if(word_occurences_in_timespan > 1):
                continue

            # If no translation is needed -> Append the word and continue
            if(target_language == self.language):
                valid_hot_words.append(
                    (hot_word, subtitles, subtitles_start, subtitles_end))
            else:
                logger.debug(f"Translating hot word '{hot_word}' From {self.language} to {target_language}.")
                response = translate_client.translate(
                    hot_word, target_language=target_language, source_language=self.language)
                translated_hot_word = clean_text(response['translatedText'])
                logger.debug(
                    f"Translation of '{hot_word}' is '{translated_hot_word}'")

                valid_hot_words.append(
                    (translated_hot_word, subtitles, subtitles_start, subtitles_end))

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
