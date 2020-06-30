from google.cloud import translate_v2 as translate
from dotenv import load_dotenv
import requests
import logging
import urllib
from logger_setup import setup_logging

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

translate_client = translate.Client()


class Translator():
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
        self.authenticated_translation = True

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

        if(self.authenticated_translation):
            response = translate_client.translate(
                string, target_language=self.target_language, source_language=self.source_language)
            results.append({'source_text': string, 'translated_text': response['translatedText']})
            return response['translatedText']

        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={self.source_language}&tl={self.target_language}&dt=t&q={urllib.parse.quote_plus(string)}"
        response = requests.get(url)
        if(response.status_code == 200):
            translated_text = response.json()[0][0][0]
            results.append({'source_text': string, 'translated_text': translated_text})
            return {'source_text': string, 'translated_text': translated_text}
        else:
            logger.debug(f'Changing to authenticated translation. Reponse status code: {response.status_code}')
            self.authenticated_translation = True
            return self.translate(string, results)