from syncit.constants import Constants
import multiprocessing as mp
import numpy as np
from moviepy.editor import VideoFileClip
from itertools import repeat
import logging
from logger_setup import setup_logging
from syncit.checker import Checker
from syncit.helpers import *
from syncit.subtitle_parser import SubtitleParser
from syncit.converter import Converter
from difflib import SequenceMatcher

setup_logging()
logger = logging.getLogger(__name__)

class DelayChecker():
    """
    Class to check the delay of subtitles and video file.

    Attributes:
    """

    def __init__(self, base64str, timestamp, subtitles):
        """
        Class to check the delay.

        Attributes:
        """

        self.converter = Converter(base64str)
        self.video = self.converter.video
        self.start = timestamp['start']
        self.end = timestamp['end']
        self.sp = SubtitleParser(subtitles)

       
    def check_delay_in_timespan(self):
        """
            Loops through the first word of each row of the subtitles in the specified timespan.
            Foreach first word, gets the transcript with radius considerations
            and compares it until it finds a match.

            Params:
                start (int): start time in seconds.
                end (int): end time in seconds.

            Returns:
                int: Subtitles delay in seconds. 
        """
              
        # Get valid hot words in timespan (reducing from the end and appending to the start the delay radius to avoid exceeding beyond the file length)
        valid_hot_words = self.sp.get_valid_hot_words(self.start, self.end)

        audio_path = self.converter.convert_video_to_audio()

        # Add to the start of each tuple in valid_hot_words the audio_path
        imap_args = [tuple([audio_path] + list(element)) for element in valid_hot_words]

        delay = None

        with mp.Pool() as pool:
            results = pool.imap_unordered(self.parse_single_hot_word, imap_args)
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
            logger.error(f'Unable to find subtitles delay in {self.start}-{self.end}.')
            self.converter.clean()
            return


                
    def parse_single_hot_word(self, args):
        """
        Gets a word and a timestamp, and tries to find the delay based on that.
        Tries to find the word time, and if found verifies that the delay is actually correct.

        Params:
            args (tuple) containing:
                audio_path (str): Path to audio file.
                hot_word (str): hot word to check.
                subtitles (str): subtitles to verify.
                subtitles_start (int): start time in seconds of the subtitles.
                subtitles_end (int): end time in seconds of the subtitles.

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
        hot_word_in_transcript = self.word_in_timespan_occurrences(audio_path, hot_word, transcript_start, transcript_end)

        # If the hot word is one time in the audio transcript, check when is it said. Else, return None
        if(hot_word_in_transcript >= 1 and hot_word_in_transcript <= Constants.MAX_OCCURENCES_TO_CHECK):
            logger.debug(f"Word '{hot_word}' is in timespan. Checking the time...")

            # Gets the word start time
            word_start_time = self.get_word_time(audio_path, hot_word, transcript_start, transcript_end, Constants.INITIAL_DELAY_CHECK_STEP)

            # If the get_word_time function couldn't find when the word is said, return None
            if(word_start_time is None):
                logger.debug(f"Continuing - unable to find the hot word '{hot_word}' in the transcript.")
                return

        else:
            logger.debug(f'Continuing - word is {hot_word_in_transcript} times in transcript, instead of 1.')
            return

        # Only got here if we have the time the hot word is said.        
        # Calculate the delay
        new_subtitles_start = word_start_time
        new_subtitles_end = subtitles_end - subtitles_start + new_subtitles_start
        subs_delay = word_start_time - subtitles_start 
        
        # Verify the sync worked
        logger.debug(f"Verifing the sync worked. Word: '{hot_word}'. Delay: {subs_delay}")
        similarity_rate = self.check_single_transcript(subtitles, new_subtitles_start, new_subtitles_end)
        if(similarity_rate < Constants.MIN_ACCURACY):
            logger.debug(f'Not accurate enough. Continuing.')
            return

        else:
            logger.info(f'Subs delay: {subs_delay}')
            return subs_delay

    
    def check_single_transcript(self, subtitles, start, end):
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

        similarity_rate = SequenceMatcher(None, clean_transcript, subtitles).ratio()
        
        logger.debug(f"""Subtitles: {subtitles} | Clean Subtitles: {subtitles} | Transcript: {clean_transcript} | Clean Transcript: {clean_transcript} | Similarity: {similarity_rate}""")

        if(similarity_rate > Constants.MIN_ACCURACY):
            return True
        return False
            

    
    def word_in_timespan_occurrences(self, audio_path, word, start, end):
        """
            Checks occurrences of a word in an audio timestamp.

            Params:
                audio_path (str): Path to audio file.
                word (str): The word.
                start (int): Start time.
                end (int): End time.
            
            Returns:
                int: Number of occurrences of word in transcript.
        """

        transcript = self.converter.convert_audio_to_text(audio_path, start, end, word)

        count = len(transcript.split())
        logger.debug(f"Checked occurrences of '{word}' in {start}-{end}. It is {count} times.")
        return count    


    def get_word_time(self, audio_path: str, word: str, start: float, end: float, step: float):
        """
        Recursive function that gets a timestamp and a word, and checks when that word is said in this timestamp.

        Params:
            audio_path (str): Path to audio file.
            word (str): Word to check.
            start (float): Start time in seconds.
            end (float): End time in seconds.
            step (float): What is the step in the for loop.

        Returns:
            float: Start time in seconds the word is said.
        """
        # End of recursive function
        if((end - start) <= Constants.MAXIMUM_WORD_LENGTH):
            return start

        # Gets the results in this section
        results = self.get_word_results_in_section(audio_path, word, start, end, step)
        if(results):
            (sections_occurences, sections_timestamps) = results
        else:
            return None

        next_action = parse_sections_occurences_results(sections_occurences)
        
        logger.debug(f"Section occurences: {sections_occurences}; Next Action: {next_action}")
        # Action == Abort
        if(next_action == 0):
            return None

        # Action - divide to three sections
        
        # Action - check middle section
        elif(next_action == 3):
            middle_start = start + (step / 3)
            middle_end = end - (step / 3)
                        
            # Calculate occurences and continue if found
            occurences = self.word_in_timespan_occurrences(audio_path, word, middle_start, middle_end)
            if(occurences == 1):
                new_step = (middle_end - middle_start) / 2
                return self.get_word_time(audio_path, word, middle_start, middle_end, new_step)
        
        # Action == Check single section
        elif(next_action == 1 or next_action == 2):     
            # Word found in two consecutive inner-section
            if(next_action == 1):
                first_winning_section = sections_occurences.index(1)
                winning_start = sections_timestamps[first_winning_section][0]
                winning_end = sections_timestamps[first_winning_section + 1][1]
                new_step = (winning_end - winning_start) / 4

            # Word found in exactly one section exactly one time
            elif(next_action == 2): 
                winning_section = sections_occurences.index(1)  
                (winning_start, winning_end) = sections_timestamps[winning_section]
                new_step = (winning_end - winning_start) / 2
                
            logger.debug(f"Word '{word}' found in timestamp {winning_start}-{winning_end}.")
            return self.get_word_time(audio_path, word, winning_start, winning_end, new_step)



    def get_word_results_in_section(self, audio_path: str, word: str, start: float, end: float, step: float):
        """
        Gets a section and a word, and divides the section to inner-sections by the step, and searches
        for the word inside each inner-section. Returns a list of the results and timestamps.

        Params:
            audio_path (str): Path to audio file.
            word (str): Word to check.
            start (float): Start time in seconds.
            end (float): End time in seconds.
            step (float): What is the step in the for loop.

        Returns:
            tuple: (sections_occurences, sections_timestamps)

            sections_occurences (list): List containing the results of how many times the word is in each inner-section.
            sections_timestamps (list): List of tuples containing (start, end) for each inner-section in sections_occurences.
        """

        logger.debug(f'Getting word time. Start:{start}; End: {end}; step: {step}.')

        # Lists containg the results from all the sections and timestamps
        sections_occurences = []
        sections_timestamps = []

        for current_start in np.arange(start, end, step):            
            
            current_end = current_start + step
            
            # Is on first run of the recursive function
            is_on_first_run = step == Constants.INITIAL_DELAY_CHECK_STEP
            
            # Only on the first run of the function add the ONE_WORD_AUDIO_TIME to the end.
            if(is_on_first_run):
                current_end += Constants.ONE_WORD_AUDIO_TIME
            
            # Make sure the last end is not larger then the given end.
            if(current_end > end):
                current_end = end

            logger.debug(f"Word '{word}' calculating occurences. End: {current_end}")
            occurrences = self.word_in_timespan_occurrences(audio_path, word, current_start, current_end)

            # Append to lists
            sections_occurences.append(occurrences)
            sections_timestamps.append((current_start, current_end))

            # Perform a check to see if aborting
            is_aborting = need_to_abort(sections_occurences, word, is_on_first_run)
            if(is_aborting):
                return None
        
        logger.debug(f"Word '{word}' ended loop.")
        return (sections_occurences, sections_timestamps)