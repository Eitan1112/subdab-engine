import os

class Constants():
    
    GOOGLE_APPLICATION_CREDENTIALS_PATH = r'‪C:\Users\Eitan\UzudurFQ' 

    MIN_ACCURACY = 0.65
    SAMPLES_TO_CHECK = 20
    SAMPLES_TO_PASS = 0.2 # 0 to 1

    DELAY_RADIUS = 22 # Seconds
    
    INITIAL_DELAY_CHECK_STEP = 2 # Seconds
    MAXIMUM_WORD_LENGTH = 1 # Seconds
    DELAY_CHECK_DIVIDER = 4
    MAX_OCCURENCES_OF_WORD_IN_RADIUS = 45

    MAX_OCCURENCES_TO_CHECK = 3

    ONE_WORD_AUDIO_TIME = 1 # How much seconds it takes to say one word (max)

    SWITCH_TO_TRIMMING_ALGO_TIME = 5

    WORD_TIME_SECTIONS_DIVIDER = 8

    DELAY_CHECKER_SECTIONS_TIME = 300 # In seconds, have to be synced with frontend

    VERIFY_DELAY_SAMPLES_TO_CHECK = 13
    VERIFY_DELAY_SAMPLES_TO_PASS = 7
    VERIFY_DELAY_TRANSLATED_SAMPLES_TO_PASS = 6

    AUDIO_LANGUAGES = [
        { 'code': 'en', 'pocketsphinx_code': 'en-US'},
        { 'code': 'it', 'pocketsphinx_code': 'it-IT'},
        { 'code': 'fr', 'pocketsphinx_code': 'fr-FR'}
    ]

    TRIM_SECTION_STEP = 0.9
    TRIM_SECTION_STEP_DIVIDER = 3
    TRIM_SECTION_FINAL_STEP = 0.1

    CHECKED_DELAY_RADIUS = 0.25

    RECIEVED_AUDIO_FILE_EXTENSION = 'm4a'
    DESIRED_AUDIO_FILE_EXTENSION = 'wav'

    MULTIPROCESSING_MINIMUM_AUDIO_LENGTH = 1 # Seconds

    COMMON_WORDS_UNSUITABLE_FOR_DETECTION = ['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 
    'for', 'on', 'are', 'with', 'as', 'i', 'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from', 'or', 'had', 'by', 'not', 
    'word', 'but', 'what', 'some', 'we', 'can', 'out', 'were', 'all', 'there', 'when', 'up', 'use', 'your', 'how', 'said', 
    'an', 'each', 'she', 'oh', 'who']

    
    SAMPLES_FOLDER = os.path.join('syncit', 'tests', 'samples')
