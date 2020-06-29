from dotenv import load_dotenv
import re
import random
from syncit.constants import Constants
from syncit.helpers import convert_subs_time, clean_text
import logging
import threading
import os
from syncit.translate import Translator
from chardet import detect as detect_encoding
from langdetect import detect as detect_language
from logger_setup import setup_logging
import uuid

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)


class SubtitleParser():
    """
    Read the subtitles and parses them for ease of use.

    Attributes:
        subtitles (str): Subtitles file content.
        re_subs (list): List of tuples containing the parsed subtitles.
        subtitles_language (str): Language of the subtitles.
        audio_language (str): Language of the audio.
        encoding (str): The encoding of the subtitles.
        translator (Translator): Translator instace with the languages loaded.
    """

    def __init__(self, subtitles_file, subtitles_language: str, audio_language: str):
        """
        Constructor for the SubtitlesParser class.

        Params:
            subtitles_file (FileStorage): File with the subtitles loaded.
            subtitles_language (str): The language of the subtitles.
            audio_language (str): The language to get the hot words in (the audio language).
        """

        subtitles_binary = subtitles_file.read()
        encoding = detect_encoding(subtitles_binary)['encoding']
        self.subtitles = subtitles_binary.decode(encoding)
        self.encoding = encoding
        logger.debug(f'Subtitles Encoding: {encoding}')
        logger.debug(f'Subtitles[:100]: {[self.subtitles[:1000]]}')
        self.read_subtitles()
        self.audio_language = audio_language

        # Detect subtitles language
        if(subtitles_language == 'ad'):  # ad = Auto Detect
            detected_language = detect_language(self.subtitles)
            logger.debug(f"Subtitles language detected as {detected_language}")

            # True if the detected language in google's supported languages
            language_items = any(map(
                lambda lang: lang['language'] == detected_language, Constants.GOOGLE_LANGUAGES))
            if(language_items is False):
                raise Exception(
                    f'Detected language {detected_language} is not supported.')
            self.subtitles_language = detected_language

        else:
            self.subtitles_language = subtitles_language

        self.translator = Translator(self.subtitles_language, audio_language)

    def read_subtitles(self):
        """
        Reads the subtitle content using regex and stores it in memory for easy access.
        """

        # Group 1: index, Group 2: Start Time, Group 3: End Time, Group 4: Text

        patterns = [
            r"(\d+)\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\n((?:.+\n)*.+)",
            r"(\d+)\r\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\r\n((?:.+\r\n)*.+)",
            # Reports pattern
            r"(\d+)\r(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\n((?:.+\r)*.+)"
        ]

        for pattern in patterns:
            re_subs = re.findall(pattern, self.subtitles, re.M | re.I)
            if(len(re_subs) > 1):
                self.re_subs = re_subs
                return

        raise Exception(
            f're_subs length is {len(re_subs)}. Maybe the regex pattern is falty?')

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
            list: The hot words.
                id (str): The word id.
                hot_word (str): Hot word.
                subtitles (str): The subtitles.
                start (float): Start time.
                end (float): End time.
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

            # Don't take numbers as hot words
            if(hot_word.replace('.', '', 1).isdigit()):  # The replace is if the number is a float
                continue

            # If no translation is needed -> Append the word and continue.
            # if(self.audio_language == self.subtitles_language):
            valid_hot_words.append({
                'id': f'{hot_word}-{uuid.uuid4().hex[:6]}',
                'hot_word': hot_word,
                'subtitles': subtitles,
                'start': subtitles_start,
                'end': subtitles_end
            })
        
        if(self.subtitles_language != self.audio_language):
            valid_hot_words = self.translate_hot_words(valid_hot_words)

        logger.debug(
            f'Hot words before filtering and sorting: {valid_hot_words}')
        valid_hot_words = self.filter_hot_words(valid_hot_words)
        return valid_hot_words
    
        

    def translate_hot_words(self, hot_words: list):
        """
        Translate hot words.

        Params:
            list: The hot words.
                id (str): The word id.
                hot_word (str): Hot word.
                subtitles (str): The subtitles.
                start (float): Start time.
                end (float): End time.
        
        Returns:
            list: The hot words translated.
                id (str): The word id.
                hot_word (str): Hot word.
                subtitles (str): The subtitles.
                start (float): Start time.
                end (float): End time.
        """       

        threads = []
        translated_hot_words = []
        results = []

        for hot_word_item in hot_words:
            thread = threading.Thread(target=self.translator.translate, args=(hot_word_item['subtitles'], results))
            thread.start()
            threads.append(thread)

        # Wait for threads to finish
        [thread.join() for thread in threads]

        for result in results:
            source_subtitles = result['source_text']
            item = [hot_word_item for hot_word_item in hot_words if hot_word_item['subtitles'] == source_subtitles][0]
            cleaned_translated_subtitles = clean_text(result['translated_text'])
            if(cleaned_translated_subtitles is None):
                continue

            item['subtitles'] = cleaned_translated_subtitles
            item['hot_word'] = cleaned_translated_subtitles.split()[0]

            if(len(item['hot_word']) < 2):
                continue

            logger.debug(
                f"Translataion. From '{self.subtitles_language}' to '{self.audio_language}'. From '{source_subtitles}' to '{item['subtitles']}'. Hot word: '{item['hot_word']}'")

            item['id'] = f'{item["hot_word"]}-{uuid.uuid4().hex[:6]}'
            translated_hot_words.append(item)
        return translated_hot_words

    def filter_hot_words(self, hot_words: list):
        """
        Filters the translated hot words, removes the falty ones.

        Params:
            hot_words (list): List of dictionaries {hot_word, subtitles, start, end}

        Returns:
            list: List of dictionaries, filter.
        """

        to_remove = []
        for hot_word_item in hot_words:
            hot_word = hot_word_item['hot_word']

            # True if the hot word is in the subtitles of it's range. (E.g. hot word 'hello' which is said at 00:42, when the subtitles at 00:52-00:56 is 'that is how you say hello')
            is_hot_word_falty = any(
                [hot_word in i['subtitles'].split() for i in hot_words if i != hot_word_item
                 and abs(i['start'] - hot_word_item['start']) < Constants.DELAY_RADIUS
                 and abs(i['end'] - hot_word_item['end']) < Constants.DELAY_RADIUS
                 ])
            if(is_hot_word_falty):
                to_remove.append(hot_word_item)

        # Can't remove them in the loop because then it will cause problems
        for item in to_remove:
            hot_words.remove(item)

        return hot_words
