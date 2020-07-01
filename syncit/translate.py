from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
import requests
import logging
import urllib
from googletrans import Translator as UnstableTranslator
from logger_setup import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

translate_client = translate.Client()


class CustomTranslator():
    """
    Class for translation purposes.

    Attributes:
        authenticated_translation (bool): Whether to use authenticated or free API.
    """

    def __init__(self, source_language: str, target_language: str):
        """
        Constructor for Translator.

        Params:
            source_langauge (str): Source language.
            target_langauge (str): Target language.
        """

        self.source_language = source_language
        self.target_language = target_language
        self.stable_translation = False

    def translate(self, string: str, results: list):
        """
        Translate a word.

        Params:
            string (str): The string to translate.
            results (list): Results to append to.

        Returns:
            dict: The translated string with the source string.
                source_text (str): The source text.
                target_text (str): The target text.
        """

        if(self.stable_translation is False):
            try:
                translator = UnstableTranslator()
                translated_text = translator.translate(string, src=self.source_language, dest=self.target_language).text
                results.append({'source_text': string, 'translated_text': translated_text})
                return translated_text
            except Exception as err:
                logger.warning(f'Unable to translate using unstable translation. Error: {err}')
                self.translation_method = False
                return self.translate(string, results)
        
        logger.debug(f'Translating using API.')
        response = translate_client.translate(
            string, target_language=self.target_language, source_language=self.source_language)
        results.append({'source_text': string, 'translated_text': response['translatedText']})
        return response['translatedText']


            