import threading
import uuid
import logging
from syncit.constants import Constants
from logger_setup import setup_logging
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

        grouped_sections = self.get_grouped_sections()
        self.get_occurences_for_grouped_sections(grouped_sections)


    def get_grouped_sections(self):
        """
        Divides the audio file to sections and gets the hot words to check for.

        Returns:
            list of dicts: List of sections with the ids to check in each timespan.
                ids (list of dicts): list of ids of words in the section.
                    id (str): The id.
                    occurences (NoneType): The occurences of the id in the timestamp.
                start (float): Start time.
                end (float): End time.
        """
        
        grouped_sections = []
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
                    section_item['ids'].append({'id': hot_word_item['id'], 'occurences': None})

            grouped_sections.append(section_item)

        # Remove Empty Sections
        grouped_sections = [section_item for section_item in grouped_sections if len(section_item['ids']) > 0]
        logger.debug(f'Sections_items {grouped_sections}')
        return grouped_sections

    def get_occurences_for_grouped_sections(self, grouped_sections: list):
        """
        Gets the occurences for the grouped sections.

        Params: 
            grouped_sections (list of dicts): The section with their hot words.
                ids (list of dicts): list of ids of words in the section.
                    id (str): The id.
                    occurences (NoneType): The occurences of the id in the timestamp.
                start (float): Start time.
                end (float): End time.
        
        Returns:
            list of dicts: The same list from the params with occurences inside.
                ids (list of dicts): list of ids of words in the section.
                    id (str): The id.
                    occurences (int): The occurences of the id in the timestamp.
                start (float): Start time.
                end (float): End time.
        """

        threads = []
        results = []
        for section_item in grouped_sections:
            start = section_item['start']
            end = section_item['end']
            ids = [item['id'] for item in section_item['ids']]
            thread = threading.Thread(target=self.get_hot_words_occurences, args=(start, end, ids, results))
            thread.start()
            threads.append(thread)

        # Wait for threads to finish
        [thread.join() for thread in threads]
        
        logger.debug(f'Final Results: {results}')
            



    def get_hot_words_occurences(self, start: float, end: float, ids: list, results: list):
        """
        Gets the occurences of the hot words inside the timespan.

        Params:
            start (float): Start time.
            end (float): End time.
            ids (list of str): List of ids.
            results (list): List to update the results (useful for threading)
        
        Appending to results:
            list of dicts:
                id (str): Id.
                occurences (int): occurences of id in timestamp.
        """
    
        hot_words = [hot_word_item['hot_word'] for hot_word_item in self.hot_words if hot_word_item['id'] in ids]
        logger.debug(f'Checking occurences. Start: {start}. End: {end}. Words: {hot_words}. Ids: {ids}.')
        transcript = self.converter.convert_audio_to_text(start, end, hot_words)
        logger.debug(f'Transcript: {transcript}')
        occurences = [{'id': id, 'occurences': transcript.split().count(hot_words[index])} for index,id in enumerate(ids)]
        logger.debug(f'Start: {start}. End: {end}. Occurences: {occurences}')
        results.append(occurences)