from moviepy.editor import AudioFileClip
import subprocess
import base64
import tempfile
import shutil
import os
import base64
import json
import requests
import uuid
import speech_recognition as sr
from syncit.constants import Constants
import logging
from syncit.constants import Constants
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


class Converter():
    """
    Class designed to make all the conversions and merges between video and audio.

    Attributes:
        audio (str): Path to audio file.
        tmpdir (str): Persistent temporary folder (if created).
        language (str): Language of the audio.
        session (requests.session): Session to persist when talking with API.
    """

    def __init__(self, audio_file, language: str):
        """
        Constructor of Converter.

        Params:
            audio_file (FileStorage): Object with the video file loaded.
            language (str): Language of the audio.
        """

        self.tmpdir = tempfile.mkdtemp()
        self.audio = self.convert_filestorage_to_file(audio_file)
        self.repair_audio_file()
        # Replace 2 char code language with 4 char code language (e.g.: en -> en-US)
        self.language = list(filter(lambda lan: lan['code'] == language ,Constants.AUDIO_LANGUAGES))[0]['pocketsphinx_code']
        self.session = requests.Session()

    def convert_filestorage_to_file(self, audio_file):
        """
        Converts FileStorage object to a file. Stores it in temporary location and returns it's path.

        Params:
            audio_file (FileStorage): Object with the video file loaded.
            extension (str): The file extension.

        Returns:
            str: Path to video file.
        """

        filename = f'{uuid.uuid4().hex[:10]}.{Constants.RECIEVED_AUDIO_FILE_EXTENSION}'
        path = os.path.join(self.tmpdir, filename)
        logger.debug(f'Converting FileStorage to file. path: {path}')
        with open(path, 'wb') as f:
            f.write(audio_file.read())

        logger.debug(f'Finished converting FileStorage to file.')
        return path

    def repair_audio_file(self):
        """
        Repairs the audio file loaded in self.audio
        The frontend gives compressed audio file, moviepy can create a new repaired file
        that will work with the speech recognition.

        Re sets the path.
        """

        logger.debug(f'Repairing audio file: {self.audio}')
        clip = AudioFileClip(self.audio)
        filename = f'{uuid.uuid4().hex[:10]}.{Constants.DESIRED_AUDIO_FILE_EXTENSION}'
        path = os.path.join(self.tmpdir, filename)
        logger.debug(f'Repairing audio file. New path: {path}')
        clip.write_audiofile(path)
        try:
            os.remove(self.audio)
            logger.debug(f'Removed file {self.audio}')
        except:
            logger.warning(f'Unable to remove file {self.audio}.')
        self.audio = path

    def convert_audio_to_text(self, start: float, end: float, hot_words: str, stop):
        """
        Converts audio file to text. Can be of specific timestamp or with hot word.

        Params:
            start (float): start time.
            end (float): end time.
            hot_words (list): hot words to look for.
            stop (function): A flag, should the function stop before (checked before sending a request).

        Returns:
            str: The required transcript.
        """

        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(self.audio)

        with audio_file as source:
            duration = end - start
            audio = recognizer.record(source, offset=start, duration=duration)

        try:
            data = {
                'frame_data_base64': base64.b64encode(audio.frame_data),
                'sample_rate': audio.sample_rate,
                'sample_width': audio.sample_width,
                'language': self.language,
                'hot_words': json.dumps(hot_words)
            }
            url = os.getenv('CONVERT_SPEECH_TO_TEXT_SERVER_URL')
            if(url is None):
                raise Exception(f'Convert speech to text server url (lambda) is None.')
            
            for _ in range(Constants.RETRIES_AFTER_API_ERROR):
                if(stop() is True):
                    return ''
                res = self.session.post(url, data=data, timeout=Constants.REQUEST_TIMEOUT)
                if(res.status_code == 200):
                    logger.debug(f'{res.text}')
                    return res.text
            raise Exception(f'Recieved status code {res.status_code} from speech to text API. Response: {res.text}.')


        except Exception as e:
            logger.error(f'Unknown Error while recognizing. Error: {e}')
            return ''

    def clean(self):
        """
        Deletes the temporary folder, if created.
        """

        if(self.tmpdir):
            try:
                shutil.rmtree(self.tmpdir)
            except:
                logger.warning(f'Unable to clean up.')
