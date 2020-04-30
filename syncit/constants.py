class Constants():
    MIN_ACCURACY = 0.65
    SAMPLES_TO_CHECK = 20
    SAMPLES_TO_PASS = 0.2 # 0 to 1

    DELAY_RADIUS = 22 # Seconds
    
    INITIAL_DELAY_CHECK_STEP = 2 # Seconds
    MAXIMUM_WORD_LENGTH = 1 # Seconds
    DELAY_CHECK_DIVIDER = 2

    MAX_OCCURENCES_TO_CHECK = 3

    ONE_WORD_AUDIO_TIME = 1 # How much seconds it takes to say one word (max)

    SWITCH_TO_TRIMMING_ALGO_TIME = 4

    WORD_TIME_SECTIONS_DIVIDER = 8

    DELAY_CHECKER_SECTIONS_TIME = 200 # In seconds, have to be synced with frontend # TODO #39 Send it in frontend

    VERIFY_DELAY_SAMPLES_TO_CHECK = 6
    VERIFY_DELAY_SAMPLES_TO_PASS = 2

    MULTIPROCESSING_MINIMUM_AUDIO_LENGTH = 1 # Seconds

    COMMON_WORDS_UNSUITABLE_FOR_DETECTION = ['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'you', 'that', 'he', 'was', 
    'for', 'on', 'are', 'with', 'as', 'i', 'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from', 'or', 'had', 'by', 'not', 
    'word', 'but', 'what', 'some', 'we', 'can', 'out', 'were', 'all', 'there', 'when', 'up', 'use', 'your', 'how', 'said', 
    'an', 'each', 'she', 'oh', 'who']


class TestConstants(Constants):
    SAMPLE_VIDEO_PATH = 'media/sample/sample.mp4'
    SAMPLE_AUDIO_PATH = 'media/sample/sample.wav'

    SAMPLE_SYNCED_PATH = 'media/sample/synced.srt'
    SAMPLE_EARLY_PATH = 'media/sample/early.srt'
    SAMPLE_LATE_PATH = 'media/sample/late.srt'

    SAMPLE_EARLY_VS_SYNCED_DELAY = 2


    SAMPLE_AUDIO_SIZE = 4090794 # Size in bytes of the WAV sample file.

    TRANSCRIPT_IN_TIMESTAMP = 'kids i am going to tell you an incredible story'
    TRANSCRIPT_FROM_SPHINX = ['kids on to tell you an incredible saw', 'kids on to tell you an incredible store']
    SUBTITLES_INDEX_FOR_TRANSCRIPT = 1
    NOT_TRANSCRIPT_IN_TIMESTAMP = 'this is some random text i am typing for the testing'
    TRANSCRIPT_TIMESTAMP_START = 4.5
    TRANSCRIPT_TIMESTAMP_END = 7.2

    SAMPLE_WORD = 'punished'
    SAMPLE_WORD_TIME = 11
    SAMPLE_WORD_TIMESTAMP = (5,15)
    SAMPLE_WORD_SECTIONS_OCCURENCES = [0, 1]
    SAMPLE_WORD_SECTIONS_TIMESTAMPS = [(5, 11.5), (10, 15)]

    SUBTITLES_SAMPLE = 'media/subtitles/sample.srt'
    SAMPLE_SUBTITLES_VALID_INDEXES = [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24]

    SAMPLE_VALID_HOT_WORDS =  [('kissing', 'kissing wont save the forest', 78.903, 80.703),
                              ('never', 'never mind', 85.643, 86.743),
                              ('quick', 'quick elsa make a prince a fancy one', 69.061, 71.861),
                              ('ugh', 'ugh anna bleugh', 76.969, 78.901)]
    SAMPLE_HOT_WORDS_START = 67
    SAMPLE_HOT_WORDS_END = 90


    LONG_SAMPLE_VIDEO = 'media/frozen/sample.mp4'
    LONG_SAMPLE_AUDIO = 'media/frozen/sample.wav'
    LONG_SAMPLE_SYNCED = 'media/frozen/synced.srt'
    LONG_SAMPLE_UNSYNCED = 'media/frozen/unsynced_frozen.srt'
    LONG_SAMPLE_DELAY = -4.3
    

    LONG_SAMPLE_WORD = 'stood'
    LONG_SAMPLE_WORD_TRANSCRIPT = 'stood a very old and very enchanted forest'
    LONG_SAMPLE_WORD_TIMESTAMP = (127.552, 131.721)
