import string
import re
import logging
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


def clean_text(original_text: str):
    """
    Cleans the text for easier comparison.
    Removes: HTML tags, texts in any brackets, text in *, music signs and punctuations.
    Replaces multiple whitespace with one, lowercase the text and trims it.

    Params:
        text (str): text to clean.

    Returns:
        str: Cleaned up text.
    """

    text = original_text

    text = text.replace('\r\n', ' ').replace('\n', ' ')

    # Remove HTML tags, text in curly, regular or square brackets and text in *
    tags = re.findall(r'((?:<|\[|\(|\*|\{).+?(?:>|\)|}|]|\*))', text)
    for tag in tags:
        text = text.replace(tag, '')

    text = text.lower()
    text = text.translate(str.maketrans(
        '', '', string.punctuation))  # Remove punctuations
    text = text.replace('♪', '').replace('â™ª', '')
    text = re.sub(' +', ' ', text)  # Replace multiple whitespaces in one
    text = text.strip()

    return text


def convert_subs_time(subs_time: str):
    """
    Converts from subtitles time to seconds.

    Params:
        subs_time (str): Subtitles time. (e.g: 00:00:38,937)

    Returns:
        int: Time in seconds.
    """

    try:
        subs_splitted = subs_time.split(':')

        hours = subs_splitted[0]
        minutes = subs_splitted[1]
        seconds = subs_splitted[2].split(',')[0]
        miliseconds = subs_splitted[2].split(',')[1]

        time = int(hours) * 3600 + int(minutes) * 60 + \
            int(seconds) + int(miliseconds) / 1000

        return time

    except:
        logger.error(f'Wrong time format in subtitles. Recieved: {subs_time}')
        raise Exception(
            f'Wrong time format in subtitles. Recieved: {subs_time}')


def list_rindex(li: list, x: object):
    """
        Gets the last index of an item in an array.

        Params:
            li (list): The list.
            x (object): The object to find the index of.

        Returns:
            int: The last index of x inside li.
    """

    for i in reversed(range(len(li))):
        if(li[i] == x):
            return i
    raise ValueError(f"{x} is not in list")


def need_to_abort(sections_occurences: list, word: str, is_first_run: bool):
    """
    Checks if the results are invalid during the for loop and needs to abort
    in the recursive function to get the word time.

    Params:
        sections_occurences (list): The results to check.
        word (str): The word (for logging purpuses).

    Returns:
        Boolean: Should you abort (True to abort, False to continue).
    """

    # If there are positive results in more then 2 sections -> Abort
    if(sections_occurences.count(0) + 2 < len(sections_occurences)):
        logger.debug(
            f"Word '{word}' more then 2 positive sections. Results: {sections_occurences} Aborting...")
        return True

    # If there are positive results in 2 sections
    if(sections_occurences.count(0) + 2 == len(sections_occurences)):
        # If one of the two positives is more then 1 time the word in the section -> Abort
        if(sections_occurences.count(1) != 2):
            logger.debug(
                f"Word '{word}' one of the positives more then 1. Aborting...")
            return True

        # If both the results are positives and 1's but they are not consecutive -> Abort
        if(sections_occurences.count(1) == 2 and sections_occurences.index(1) + 1 != list_rindex(sections_occurences, 1)):
            logger.debug(f"Word '{word}' two 1's not consecutive. Aborting...")
            return True

    # If there are positive results in 1 section and this result is more then one and this is the first run -> Abort
    if(sections_occurences.count(0) + 1 == len(sections_occurences) and sections_occurences.count(1) == 0 and is_first_run):
        logger.debug(
            f"Word '{word}' was more then one time in one section on the initial run. Aborting.")
        return True

    logger.debug(f"Word '{word}' is good. {sections_occurences} Continuing..")
    return False


def parse_sections_occurences_results(sections_occurences: list):
    """
    Parses the section occurences results to check what the desired action
    should be.

    Params:
        sections_occurences (list): The occurences of a specific word inside the inner-sections of a specific section.

    Returns:
        int: The action to perform.
        0 - abort
        1 - check one section but divide to four inner-sections because of consecutive 1s
        2 - check the one section found.
        3 - check middle section because the timespan is divided to 2 sections and both empty

    """

    # Word found in more then one section
    if(sections_occurences.count(1) > 1):
        # If word is in two consecutive sections -> check the middle section
        if(sections_occurences.count(1) == 2 and sections_occurences.index(1) + 1 == list_rindex(sections_occurences, 1)):
            return 1

        # else -> abort
        else:
            return 0

    # Word not found in any section.
    elif(1 not in sections_occurences):
        # If the current timespan is divided to 2 sections -> check middle section
        if(len(sections_occurences) == 2):
            return 3
        # The current timespan is divided to more then 2 sections -> abort
        else:
            return 0

    # Word found in exactly one section
    return 2
