import re
import random
from syncit.constants import Constants
from syncit.helpers import *
import logging
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


class SubtitleParser():
    """
    Read the subtitles and parses them for ease of use.

    Attributes:
        path (str): Path to subtitles file.
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
        Reads the subtitle file and stores it in memory for easy access.
        """

        pattern = r"(\d+)\r\n(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)\r\n((?:.+\r\n)*.+)" # Group 1: index, Group 2: Start Time, Group 3: End Time, Group 4: Text

        re_subs = re.findall(pattern, self.subtitles, re.M|re.I)

        self.re_subs = re_subs
        

    def get_subtitles(self, index: int):
        """
        Gets cleaned subtitles and the timespan of a specific index.

        Params:
            index (int): Index

        Returns:
            tuple: (subtitles, start, end)
        """

        match = self.re_subs[index - 1]
        start = convert_subs_time(match[1])
        end = convert_subs_time(match[2])
        subtitles = match[3]
        subtitles = clean_text(subtitles)

        return (subtitles, start, end)

    
    def get_valid_indexes(self):
        """
        Get list of valid indexes from the loaded subtitles.
        Valid indexes are indexes where the cleaned subtitles aren't
        an empty string.

        Returns:
            list: List of the indexes.
        """

        # Gets number of rows in the subtitles
        subs_length = len(self.re_subs)
        
        # If there are less rows then the desired amount to check -> Set it to the number of rows
        samples_to_check = Constants.SAMPLES_TO_CHECK
        if(subs_length < Constants.SAMPLES_TO_CHECK):
            samples_to_check = subs_length

        # Gets random indexes from the range
        #indexes_to_check = random.sample(range(1, subs_length), samples_to_check)
        invalids = []
        indexes_to_check = []

        while len(indexes_to_check) != samples_to_check:

            # If checked all the numbers in the range and not enough found valid -> raise
            if(len(indexes_to_check) + len(invalids) == subs_length):
                raise Exception('Unable to find enough samples to test.')
            
            # Get random index
            index = random.randint(1, subs_length)

            # Check if it was already parsed
            if(index not in invalids and index not in indexes_to_check):
                # Get cleaned subtitles
                cleaned_subs= self.get_subtitles(index)[0]
                if(cleaned_subs == ''):
                    invalids.append(index)
                else:
                    indexes_to_check.append(index)

        return indexes_to_check
        
    
    def sync_subtitles(self, delay: float, path: str):
        """
        Create new file with synced timings according to the delay.

        Params:
            delay (float): delay in seconds.
            path (str): path to write the file.
        """
            
        new_subtitles = ''

        # Read old subtitles
        with open(self.subtitles, 'r') as subs_file:
            for row in subs_file:
                # Search for timestamps
                time_line_pattern = r'(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})' # Match the pattern 00:00:06,181 --> 00:00:08,383
                match = re.findall(time_line_pattern, row)
                
                # If row is not timestamp
                if(match == []):
                    new_subtitles += row
                    continue

                # If row is timestamp -> Calculate new time and append
                start_time = add_delay(match[0][0], delay)
                end_time = add_delay(match[0][1], delay)
                row = f'{start_time} --> {end_time}\n'
                new_subtitles += row

        with open(path, 'w') as f:
            f.write(new_subtitles)


    def get_valid_hot_words(self, start: float, end: float):
        """
        Loops through the subtitles and finds valid hot words in the specified timespan.

        Params:
            start (float): start time.
            end (float): end time.

        Returns:
            list: A List of tuples containing: (hot word, subtitles, start, end).
        """

        valid_hot_words = []

        subs_length = len(self.re_subs)
        logger.debug(f'Subs length: {subs_length}')

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

            
            valid_hot_words.append((hot_word, subtitles, subtitles_start, subtitles_end))

        return valid_hot_words