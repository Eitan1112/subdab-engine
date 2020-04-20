from moviepy.editor import AudioFileClip
import subprocess
import base64
import tempfile
import shutil
import os
import base64
import uuid
import speech_recognition as sr
from syncit.constants import Constants
import logging
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


class Converter():
    """
    Class designed to make all the conversions and merges between video and audio.

    Attributes:
        video (str): Path to video file.
        tmpdir (str): Persistent temporary folder (if created).
    """

    def __init__(self, base64str: str, extension: str):
        """
        Constructor of Converter.

        Params:
            base64str (str): Base64 string of the file.
            extension (str): The file extension.
        """

        self.tmpdir = tempfile.mkdtemp()
        self.video = self.convert_base64_to_file(base64str, extension)

    def convert_base64_to_file(self, base64str: str, extension: str):
        """
        Converts base64 string to a file. Stores it in temporary location and returns it's path.

        Params:
            base64 (str): Base64 string.
            extension (str): The file extension.

        Returns:
            str: Path to video file.
        """

        # TODO #8 Find Format Aloneee
        filename = f'{uuid.uuid4().hex[:10]}.{extension}'
        path = os.path.join(self.tmpdir, filename)
        logger.debug(f'Converting base64 to file. path: {path}')
        with open(path, 'wb') as f:
            try:
                f.write(base64.b64decode(base64str))
            except Exception as e:
                logger.error(f'Unable to decode base64 string. Error: {e}')

        return path

    def convert_video_to_audio(self):
        """
        Converts the video file to audio file. (wav format).
        Creates a temporary folder if doesn't exists.

        Returns:
            str: Path to audio file. 
        """

        logger.debug(f"Converting video to audio.")

        # If there isn't a temporary folder, create one.
        if(self.tmpdir is None):
            self.tmpdir = tempfile.mkdtemp()

        audio_filename = f'Temporary.wav'
        audio_path = os.path.join(self.tmpdir, audio_filename)

        try:
            # Convert
            audio = AudioFileClip(self.video)
            audio.write_audiofile(audio_path)
            return audio_path
        except Exception as e:
            logger.error(
                f'Unable to create audio clip from video file. Path: {self.video}')

    def convert_video_to_text(self, start=None, end=None):
        """
        Gets the transcript of the audio at a certain timespan.
        Cuts the video -> convert it to audio -> gets the transcript > remove audio.

        Params:
            start (float): Start time of the check.
            end (float): End time of the check.

        Returns:
            str: The transcript of this audio at this timespan.
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_filename = f'Temporary.wav'

            audio_path = os.path.join(tmpdir, audio_filename)

            try:
                audio = AudioFileClip(self.video)

                # Create subclip with the desired length and get transcript
                logger.debug(f'Writing to audio file {audio_path}')
                if(start and end):
                    if(start < 0):
                        start = 0
                    if(end > audio.duration):
                        end = audio.duration
                    audio.subclip(start, end).write_audiofile(audio_path)
                else:
                    audio.write_audiofile(audio_path)

                transcript = self.convert_audio_to_text(audio_path)
                return transcript
            except Exception as e:
                logger.error(
                    f'Error while converting video to text. Error: {e}')

    def convert_audio_to_text(self, audio_path: str, start=None, end=None, hot_word=None):
        """
        Converts audio file to text. Can be of specific timestamp or with hot word.

        Params:
            audio_path (str): Path to audio file.
            start (float): OPTIONAL: start time.
            end (float): OPTIONAL: end time.
            hot_word (str): OPTIONAL: hot word to look for.

        Returns:
            str: The required transcript.
        """

        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(audio_path)

        with audio_file as source:
            if(start and end):
                duration = end - start
                audio = recognizer.record(
                    source, offset=start, duration=duration)
            else:
                audio = recognizer.record(source)

        try:
            if(hot_word):
                transcript = recognizer.recognize_sphinx(
                    audio, 'en-US', [(hot_word, 1)])
            else:
                transcript = recognizer.recognize_sphinx(audio)
            return transcript

        # Empty transcript
        except sr.UnknownValueError:
            return ''

        except Exception as e:
            logger.error(f'Unknown Error while recognizing. Error: {e}')
            return ''

    def clean(self):
        """
        Deletes the temporary folder, if created.
        """

        if(self.tmpdir):
            shutil.rmtree(self.tmpdir)
