import unittest
from syncit.helpers import *


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
    

    def test_convert_seconds_time(self):
        """
        Test for testing the convert_seeconds_time method.
        """

        sample_time = 8406.181
        time = convert_seconds_time(sample_time)
        self.assertEqual(time, '02:20:06,181')


    def test_add_delay(self):
        """
        Test for testing the add_delay method.
        """

        sample_time = '02:20:06,181'
        delay = 2150
        new_time = add_delay(sample_time, delay)
        self.assertEqual(new_time, '02:55:56,181')

        
    def test_list_rindex(self):
        """
        Test for the list_rindex method.
        """

        sample_list = ['m', 'a', 'e', 'a', 'e', 'x']

        e_rindex = list_rindex(sample_list, 'e')
        self.assertEqual(e_rindex, 4)

        a_rindex = list_rindex(sample_list, 'a')
        self.assertEqual(a_rindex, 3)

        x_rindex = list_rindex(sample_list, 'x')
        self.assertEqual(x_rindex, 5)

        with self.assertRaises(ValueError):
            p_rindex = list_rindex(sample_list, 'p')
        

    def test_need_to_abort(self):
        """
        Test for the need_to_abort method.
        """

        sample_word = 'sample_word'        
        samples = [
            # (Result, sections_occurences, word, is_first_run)
            (True, [0,1,1,1,0], sample_word, False),
            (True, [0,1,1,1,0], sample_word, True),
            (True, [1,0,0,1,2], sample_word, False),
            (True, [1,1,1], sample_word, True),
            (True, [0,1,0,1,0,0], sample_word, True),
            (True, [0,1,2,0,0], sample_word, True),
            (True, [1,2], sample_word, False),
            (True, [2,0,0,0], sample_word, True),
            (False, [2,0,0,0], sample_word, False),
            (False, [1,0,0,0,0], sample_word, False),
            (False, [0], sample_word, False),
            (False, [2], sample_word, False),
            (False, [0,1,1,0], sample_word, False)
        ]

        for sample in samples:
            (desired_result, sections_occurences, word, is_first_run) = sample
            result = need_to_abort(sections_occurences, word, is_first_run)
            self.assertEqual(result, desired_result, sample)