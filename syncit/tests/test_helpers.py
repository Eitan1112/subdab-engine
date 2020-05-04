import unittest
from syncit.helpers import clean_text, convert_subs_time


class TestChecker(unittest.TestCase):
    """
    Class for testing the checker class.

    Attributes:
        synced_checker (object): Checker object with synced subtitles
        early_checker (object): Checker object with early subtitles
        late_checker (object): Check object with late subtitles
    """

    def test_clean_text(self):
        """
        Test for clean_text method.
        """

        texts_to_clean = (
            '<i>(QUACK)</i>',
            'Some Text',
            '♪ Hello Hello ♪',
            '[Some text]',
            '<i><span font="helavica">Adios</span></i>',
            'What?\nThis is WHAT?',
            ' Some   text in   multiple     whitespaces ',
            '<i>*Quacks*</i>'        
        ) 

        target_texts = (
            '',
            'some text',
            'hello hello',
            '',
            'adios',
            'what this is what',
            'some text in multiple whitespaces',
            ''
        )

        for i,text in enumerate(texts_to_clean):
            cleaned_text = clean_text(text)
            self.assertEqual(cleaned_text, target_texts[i])

    
    def test_convert_subs_time(self):
        """
        Test for testing the convert_subs_time method. 
        """

        sample_time = '02:20:06,181'
        time = convert_subs_time(sample_time)
        self.assertEqual(time, 8406.181)
