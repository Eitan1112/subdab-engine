import random
import ctypes
import threading
import time
import uuid
import logging
import numpy as np
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
        self.sp = SubtitleParser(
            subtitles_file, subtitles_language, audio_language)
        self.audio_language = audio_language
        self.subtitles_language = subtitles_language
        self.hot_words = self.sp.get_valid_hot_words(start, end)
        logger.debug(f'Hot words: {self.hot_words} start: {start} end: {end}')
        self.falty_delays = []
        self.checked = []

    def check_delay(self):
        """
        Check the delay.

        Returns:
            float: The delay.
        """

        self.hot_words = self.filter_hot_words()
        if(len(self.hot_words) < Constants.VERIFY_DELAY_SAMPLES_TO_CHECK):
            logger.debug(f'Not enough hot words, aborting.')
            return
        grouped_sections = self.get_grouped_sections()
        grouped_sections = self.get_occurences_for_grouped_sections(
            grouped_sections)
        grouped_sections = self.filter_grouped_sections(grouped_sections)

        for section in grouped_sections:
            section_ids = [item['id'] for item in section['ids']]
            trimmed_results = self.trim_section(
                section['start'], section['end'], section_ids)
            if(trimmed_results == None):
                continue
            verified_trimmed_results = self.verify_trimmed_results(
                trimmed_results)

            for trimmed_result in verified_trimmed_results:
                # Find the original time of the word in the subtitles
                subtitles_start = [hot_word_item['start']
                                   for hot_word_item in self.hot_words if hot_word_item['id'] == trimmed_result['id']][0]
                delay = trimmed_result['start'] - subtitles_start
                logger.debug(
                    f'Verifing delay {delay} of word id {trimmed_result["id"]}. Checked: {self.checked}')
                is_verified = self.verify_delay(delay)
                if(is_verified):
                    return delay

    def filter_hot_words(self):
        """
        Filter the hot words based on occurences in specific timespan.

        Returns:
            list of dicts: The hot words without the falty ones.
        """

        threads = []
        results = []

        for start in range(self.start, self.end, Constants.FILTER_HOT_WORDS_SECTION):
            end = start + Constants.FILTER_HOT_WORDS_SECTION + \
                Constants.FILTER_HOT_WORDS_ADD_TO_END
            sections_ids = [hot_word_item['id'] for hot_word_item in self.hot_words if hot_word_item['start'] >
                            start and hot_word_item['end'] < end - Constants.FILTER_HOT_WORDS_ADD_TO_END]
            transcript_start = start % Constants.DELAY_CHECKER_SECTIONS_TIME
            transcript_end = end % Constants.DELAY_CHECKER_SECTIONS_TIME
            thread = threading.Thread(target=self.get_hot_words_occurences, args=(
                transcript_start, transcript_end, sections_ids, results))
            thread.start()
            threads.append(thread)

        # Wait for threads to finish
        [thread.join() for thread in threads]
        filtered_hot_words_ids = [item['id'] for section in results for item in section['ids']
                                  if item['occurences'] > 0 and item['occurences'] < Constants.FILTER_HOT_WORDS_MAXIMUM_OCCURENCES]
        filtered_hot_words = [
            hot_word_item for hot_word_item in self.hot_words if hot_word_item['id'] in filtered_hot_words_ids]
        logger.debug(f'Filtered hot words: {filtered_hot_words}')
        return filtered_hot_words

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
            section_end = section_start + Constants.DIVIDED_SECTIONS_TIME + \
                Constants.ONE_WORD_AUDIO_TIME
            if(section_end > self.end):
                section_end = self.end  # Handle edge case where the end time is after the audio end time
            section_item = {'ids': [],
                            'start': section_start, 'end': section_end}

            # Append ids of hot words inside timespan
            for hot_word_item in self.hot_words:
                hot_word_start = hot_word_item['start'] - \
                    Constants.DELAY_RADIUS
                hot_word_end = hot_word_item['end'] + Constants.DELAY_RADIUS
                is_word_in_section = hot_word_start < section_end and hot_word_end > section_start
                if(is_word_in_section):
                    section_item['ids'].append(
                        {'id': hot_word_item['id'], 'occurences': None})

            grouped_sections.append(section_item)

        # Remove Empty Sections
        grouped_sections = [section_item for section_item in grouped_sections if len(
            section_item['ids']) > 0]
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
            thread = threading.Thread(
                target=self.get_hot_words_occurences, args=(start, end, ids, results))
            thread.start()
            threads.append(thread)

        # Wait for threads to finish
        [thread.join() for thread in threads]

        logger.debug(f'Grouped Results with occurences: {results}')
        return results

    def filter_grouped_sections(self, grouped_sections):
        """
        Filter the grouped sections and remove falty ones.

        Params:
            grouped_sections (list of dicts): The section with their hot words.
                start (float): Start time.
                end (float): End time.
                ids (list of dicts): list of ids of words in the section.
                    id (str): The id.
                    occurences (int): The occurences of the id in the timestamp.

        Returns:
            (list of dicts): The grouped sections without falty words.
                ids (list of dicts): list of ids of words in the section.
                    id (str): The id.
                    occurences (int): The occurences of the id in the timestamp.
                start (float): Start time.
                end (float): End time.
        """

        # Remove words who in at least one section, they were found more then the threshold set
        ids_to_remove = [item['id'] for section in grouped_sections for item in section['ids']
                         if item['occurences'] > Constants.MAX_OCCURENCES_IN_ONE_SECTION]
        logger.debug(f'ids to remove: {ids_to_remove}')

        ids_of_grouped_sections = [
            item['id'] for section in grouped_sections for item in section['ids'] if item['occurences'] > 0]
        ids_to_remove += [id for id in ids_of_grouped_sections if ids_of_grouped_sections.count(
            id) > Constants.MAX_OCCURENCES_FOR_ONE_WORD]

        filtered_grouped_results = []
        for section in grouped_sections:
            filtered_section = {
                'start': section['start'], 'end': section['end'], 'ids': []}
            for item in section['ids']:
                # Remove word from ids_to_remove
                if(item['id'] not in ids_to_remove and item['occurences'] != 0):
                    filtered_section['ids'].append(item)

            if(len(filtered_section['ids']) > 0):
                filtered_grouped_results.append(filtered_section)

        logger.debug(f'Filtered Grouped Results: {filtered_grouped_results}')
        return filtered_grouped_results

    def trim_section(self, start, end, ids):
        """
        Trim a section of hot words.

        Params:
            start (float): Start time.
            end (float): End time.
            ids (list of str): IDs to check for.

        Returns:
            list of dicts: The ids and their start time.
                id (str): ID of word.
                start (float): Start time of id after being trimmed.
        """

        logger.debug(
            f'Start trimming. Start: {start}. End: {end}. Ids: {ids}.')
        results = []
        stop = False
        threads = []
        for current_start in np.arange(start, end, Constants.TRIM_SECTION_STEP):
            thread = threading.Thread(target=self.get_hot_words_occurences, args=(
                current_start, end, ids, results, lambda: stop))
            thread.start()
            threads.append(thread)

        while True:
            final_ids_times = []
            sorted_results = sorted(
                results, key=lambda result: result['start'])
            for idx, single_timestamp_results in enumerate(sorted_results[:-1]):
                for current_result in single_timestamp_results['ids']:
                    if(current_result['occurences'] != 1):
                        continue
                    for next_result in results[idx + 1]['ids']:
                        if(next_result['id'] == current_result['id'] and next_result['occurences'] == 0):
                            final_ids_times.append(
                                {'id': current_result['id'], 'start': single_timestamp_results['start']})
                            if(len(final_ids_times) == len(ids)):
                                stop = True
                                logger.debug(
                                    f'Final ids times returned: {final_ids_times}.')
                                return final_ids_times

            # Break loop if all threads are finished
            if(len(results) == len(threads)):
                break

        logger.error(
            f'Unable to find trimmed time. Results: {sorted_results}. Final ids times: {final_ids_times}')

    def verify_trimmed_results(self, trimmed_results):
        """
        Verifies the trimming results before verifing a delay.

        Params:
            trim_results (list of dicts): The ids and their start time.
                id (str): ID of word.
                start (float): Start time of id after being trimmed.

        Returns:
            list of dicts: Same list without falty times.
        """

        logger.debug(f'Verifing trimmed results: {trimmed_results}')
        threads = []
        occurences_results = []

        for result in trimmed_results:
            logger.debug(f'Verifing result: {result}.')
            thread = threading.Thread(target=self.get_hot_words_occurences, args=(
                result['start'], result['start'] + Constants.ONE_WORD_AUDIO_TIME, [result['id']], occurences_results))
            thread.start()
            threads.append(thread)

        # Wait for threads to finish
        [thread.join() for thread in threads]

        verified_trimmed_results = []
        for result in occurences_results:
            if(result['ids'][0]['occurences'] > 0):
                verified_trimmed_results.append(
                    {'id': result['ids'][0]['id'], 'start': result['start']})

        logger.debug(f'Verified trimmed results: {verified_trimmed_results}')
        return verified_trimmed_results

    def verify_delay(self, delay: float):
        """
        Checks if the delay is correct.

        Params:
            delay (float): The delay.                

        Returns:
            bool: Whether the delay is correct or not.
        """

        logger.debug(f'Starting to verify delay: {delay}')
        similars = 0
        unsimilars = 0
        hot_words = self.hot_words[:]
        random.shuffle(hot_words)
        samples_to_check = Constants.VERIFY_DELAY_SAMPLES_TO_CHECK
        hot_words = hot_words[:samples_to_check]
        logger.debug(f'Hot words to check: {hot_words}')
        threads = []
        results = []
        stop = False

        # Check if the hot words are translated. If so -> Change the samples to pass amount.
        if(self.audio_language == self.subtitles_language):
            samples_to_pass = Constants.VERIFY_DELAY_SAMPLES_TO_PASS
        else:
            samples_to_pass = Constants.VERIFY_DELAY_TRANSLATED_SAMPLES_TO_PASS

        for hot_word_item in hot_words:
            transcript_start = (hot_word_item['start'] %
                                Constants.DELAY_CHECKER_SECTIONS_TIME) + delay
            transcript_end = transcript_start + Constants.ONE_WORD_AUDIO_TIME

            thread = threading.Thread(target=self.get_hot_words_occurences, args=(
                transcript_start, transcript_end, [hot_word_item['id']], results, lambda: stop))
            thread.start()
            threads.append(thread)

        logger.debug(f'Started {len(threads)} threads')
        while True:
            similars = len(
                [result for result in results if result['ids'][0]['occurences'] > 0])
            unsimilars = len(results) - similars
            if(similars >= samples_to_pass):
                logger.debug(f'Found delay: {delay}')
                stop = True
                return True

            if(unsimilars >= samples_to_check - samples_to_pass):
                # Add delay to falty occurences. Replace the first index of None in the list with the delay.
                self.falty_delays.append(float(delay))
                logger.debug(
                    f"Added {delay} to falty delays. Results: {results} Falty delays: {self.falty_delays}")
                stop = True
                return False

    def get_hot_words_occurences(self, start: float, end: float, ids: list, results: list, stop=lambda: False):
        """
        Gets the occurences of the hot words inside the timespan.

        Params:
            start (float): Start time.
            end (float): End time.
            ids (list of str): List of ids.
            results (list): List to update the results (useful for threading)
            stop (function): Should the converter stop before sending the request. If not passed, will not stop.

        Appending to results:
            list of dicts:
                start (float): Start time.
                end (float): End time.
                ids (list of dicts): 
                    id (str): ID of hot word.
                    occurences (int): occurences of id in timestamp.
        """

        ids_checked = [id for id in ids for checked in self.checked if id == checked['id']
                       and start >= checked['start'] and end <= checked['end'] and checked['occurences'] == 0]

        # Get words from ids
        hot_words = [hot_word_item['hot_word']
                     for hot_word_item in self.hot_words if hot_word_item['id'] in ids]

        if(len(ids_checked) == len(ids)):
            timespan_result = [{'id': id, 'occurences': 0}
                               for index, id in enumerate(ids)]
            # logger.debug(f"Already checked. Checking: {start}-{end}-{ids}. Checked: {[checked for id in ids for checked in self.checked if id == checked['id'] and start >= checked['start'] and end <= checked['end'] and checked['occurences'] == 0]}")

        else:
            transcript = self.converter.convert_audio_to_text(
                start, end, hot_words, stop)
            timespan_result = [{'id': id, 'occurences': transcript.split().count(
                hot_words[index])} for index, id in enumerate(ids)]
            # logger.debug(f"Adding to checked: {[{'start': start, 'end': end, 'id': item['id'], 'occurences': item['occurences']} for item in timespan_result]}")
            self.checked += [{'start': start, 'end': end, 'id': item['id'],
                              'occurences': item['occurences']} for item in timespan_result if item['occurences'] == 0]

        logger.debug(
            f"Checked Occurences: {({'start': start, 'end': end, 'ids': timespan_result})}.")
        results.append({'start': start, 'end': end, 'ids': timespan_result})
