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
        logger.warning(f'Wrong time format in subtitles. Recieved: {subs_time}')


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
    logger.warning(f'{i} is not in the list (rindex_list).')