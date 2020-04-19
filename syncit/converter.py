from moviepy.editor import VideoFileClip
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

    def __init__(self, base64str):
        """
        Constructor of Converter.

        Params:
            base64str (str): Base64str of the file.
        """
        
        self.tmpdir = tempfile.mkdtemp()
        self.video = self.convert_base64_to_file(base64str)
        

    def check_extension(self):
        """
        Checks if the extension of the video file is valid.

        Returns:
            Boolean: Whether the extension is supported or not.
        """

        extension = self.video.split('.')[-1]
        if(extension in Constants.SUPPORTED_VIDEO_FORMATS):
            return True
        return False


    def convert_base64_to_file(self, base64str):
        """
        Converts base64 string to a file. Stores it in temporary location
        and returns it's path.

        Params:
            base64 (str): Base64 string.

        Returns:
            str: Path to video file.
        """

        filename = uuid.uuid4().hex[:10]
        path = os.path.join(self.tmpdir, filename)
        logger.debug(f'Converting base64 to file. path: {path}')
        with open(path, 'wb') as f:
            f.write(base64.b64decode(base64str))

        return path        
    

    def convert_video_to_audio(self, start=None , end=None ):
        """
        Converts the video file to audio file in the specified timespan (wav format).
        Creates a temporary folder if doesn't exists.

        Params:
            start (float): Start time in seconds.
            end (float): End time in seconds.

        Returns:
            str: Path to audio file. 
        """

        logger.debug(f"Converting video to audio. {start}-{end}")

        # If there isn't a temporary folder, create one.        
        if(self.tmpdir is None):
            self.tmpdir = tempfile.mkdtemp()

        # Generate uniqe filename
        audio_filename = f'{end}{start}.wav'

        audio_path = os.path.join(self.tmpdir, audio_filename)

        video = VideoFileClip(self.video)
        
        # Validate start and end times
        if(not start or start < 0):
            start = 0

        if(not end or end > video.duration):
            end = video.duration

        # Convert
        video.subclip(start, end).audio.write_audiofile(audio_path)

        return audio_path

    
    def convert_video_to_text(self, start=None, end=None, hot_word=None):
        """
        Gets the transcript of the audio at a certain timespan.
        Cuts the video -> convert it to audio -> gets the transcript > remove audio.

        Params:
            start (float): Start time of the check.
            end (float): End time of the check.
            hot_word (str): If specified, look only for this word.

        Returns:
            str: The transcript of this audio at this timespan.
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            audio_filename = f'{end}{start}.wav'

            audio_path = os.path.join(tmpdir, audio_filename)

            video = VideoFileClip(self.video)

            # Validate start and end times
            if(start < 0):
                start = 0
            if(end > video.duration):
                end = video.duration

            # Create subclip with the desired length and get transcript
            if(start and end):
                video.subclip(start, end).audio.write_audiofile(audio_path)            
            else:
                video.audio.write_audiofile(audio_path)

            transcript = self.convert_audio_to_text(audio_path, hot_word=hot_word)
            return transcript
            
        
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
                audio = recognizer.record(source, offset=start, duration=duration)
            else:
                audio = recognizer.record(source)

        try:
            if(hot_word):
                transcript = recognizer.recognize_sphinx(audio, 'en-US', [(hot_word, 1)])
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