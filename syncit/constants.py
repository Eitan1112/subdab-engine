import os


class Constants():
    # MIN_ACCURACY = 0.65
    # SAMPLES_TO_CHECK = 20
    # SAMPLES_TO_PASS = 0.2  # 0 to 1

    DELAY_RADIUS = 22  # Seconds

    # INITIAL_DELAY_CHECK_STEP = 2  # Seconds
    # MAXIMUM_WORD_LENGTH = 1  # Seconds
    # DELAY_CHECK_DIVIDER = 4
    # MAX_OCCURENCES_OF_WORD_IN_RADIUS = 45

    # MAX_OCCURENCES_TO_CHECK = 3

    ONE_WORD_AUDIO_TIME = 1  # How much seconds it takes to say one word (max)

    # SWITCH_TO_TRIMMING_ALGO_TIME = 5

    # WORD_TIME_SECTIONS_DIVIDER = 8

    # In seconds, have to be synced with frontend.
    DELAY_CHECKER_SECTIONS_TIME = 300
    # After verifing X delays, send a response without delay to recieve new timestamp.
    MAXIMUM_DELAYS_TO_VERIFY = 15

    VERIFY_DELAY_SAMPLES_TO_CHECK = 13
    VERIFY_DELAY_SAMPLES_TO_PASS = 5
    VERIFY_DELAY_TRANSLATED_SAMPLES_TO_PASS = 4

    AUDIO_LANGUAGES = [
        {'code': 'en', 'pocketsphinx_code': 'en-US'},
        {'code': 'it', 'pocketsphinx_code': 'it-IT'},
        {'code': 'fr', 'pocketsphinx_code': 'fr-FR'},
        { 'code': 'es', 'pocketsphinx_code': 'es-ES'},
        { 'code': 'mx', 'pocketsphinx_code': 'es-MX'},
        { 'code': 'de', 'pocketsphinx_code': 'de-DE'},
        { 'code': 'el', 'pocketsphinx_code': 'el-GR'},
        { 'code': 'hi', 'pocketsphinx_code': 'hi-HI'},
        { 'code': 'kz', 'pocketsphinx_code': 'kz-KZ'},
        { 'code': 'nl', 'pocketsphinx_code': 'nl-NL'},
        { 'code': 'ru', 'pocketsphinx_code': 'ru-RU'},
        { 'code': 'zh', 'pocketsphinx_code': 'zh-CN'},
    ]

    # TRIM_SECTION_STEP = 0.9
    TRIM_SECTION_STEP_DIVIDER = 3
    TRIM_SECTION_FINAL_STEP = 0.1

    CHECKED_DELAY_RADIUS = 0.25

    RECIEVED_AUDIO_FILE_EXTENSION = 'm4a'
    DESIRED_AUDIO_FILE_EXTENSION = 'wav'

    MULTIPROCESSING_MINIMUM_AUDIO_LENGTH = 1  # Seconds

    COMMON_WORDS_UNSUITABLE_FOR_DETECTION = ['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'you', 'that', 'he', 'was',
                                             'for', 'on', 'are', 'with', 'as', 'i', 'his', 'they', 'be', 'at', 'one', 'have', 'this', 'from', 'or', 'had', 'by', 'not',
                                             'word', 'but', 'what', 'some', 'we', 'can', 'out', 'were', 'all', 'there', 'when', 'up', 'use', 'your', 'how', 'said',
                                             'an', 'each', 'she', 'oh', 'who']

    SAMPLES_FOLDER = os.path.join('syncit', 'tests', 'samples')

    ##### New Delay Checker #####
    FILTER_HOT_WORDS_SECTION = 35
    FILTER_HOT_WORDS_ADD_TO_END = 10
    FILTER_HOT_WORDS_MAXIMUM_OCCURENCES = 45
    DIVIDED_SECTIONS_TIME = 4
    RETRIES_AFTER_API_ERROR = 4
    MAX_OCCURENCES_IN_ONE_SECTION = 5
    MAX_OCCURENCES_FOR_ONE_WORD = 6
    TRIM_SECTION_STEP = 0.2
    REQUEST_TIMEOUT = 8


    GOOGLE_LANGUAGES = [{'language': 'af', 'name': 'Afrikaans'},  
                        {'language': 'sq', 'name': 'Albanian'},   
                        {'language': 'am', 'name': 'Amharic'},    
                        {'language': 'ar', 'name': 'Arabic'},     
                        {'language': 'hy', 'name': 'Armenian'},   
                        {'language': 'az', 'name': 'Azerbaijani'},
                        {'language': 'eu', 'name': 'Basque'},     
                        {'language': 'be', 'name': 'Belarusian'}, 
                        {'language': 'bn', 'name': 'Bengali'},    
                        {'language': 'bs', 'name': 'Bosnian'},    
                        {'language': 'bg', 'name': 'Bulgarian'},  
                        {'language': 'ca', 'name': 'Catalan'},    
                        {'language': 'ceb', 'name': 'Cebuano'},   
                        {'language': 'ny', 'name': 'Chichewa'},   
                        {'language': 'zh-CN', 'name': 'Chinese (Simplified)'},
                        {'language': 'zh-TW', 'name': 'Chinese (Traditional)'},
                        {'language': 'co', 'name': 'Corsican'},
                        {'language': 'hr', 'name': 'Croatian'},
                        {'language': 'cs', 'name': 'Czech'},
                        {'language': 'da', 'name': 'Danish'},
                        {'language': 'nl', 'name': 'Dutch'},
                        {'language': 'en', 'name': 'English'},
                        {'language': 'eo', 'name': 'Esperanto'},
                        {'language': 'et', 'name': 'Estonian'},
                        {'language': 'tl', 'name': 'Filipino'},
                        {'language': 'fi', 'name': 'Finnish'},
                        {'language': 'fr', 'name': 'French'},
                        {'language': 'fy', 'name': 'Frisian'},
                        {'language': 'gl', 'name': 'Galician'},
                        {'language': 'ka', 'name': 'Georgian'},
                        {'language': 'de', 'name': 'German'},
                        {'language': 'el', 'name': 'Greek'},
                        {'language': 'gu', 'name': 'Gujarati'},
                        {'language': 'ht', 'name': 'Haitian Creole'},
                        {'language': 'ha', 'name': 'Hausa'},
                        {'language': 'haw', 'name': 'Hawaiian'},
                        {'language': 'iw', 'name': 'Hebrew'},
                        {'language': 'hi', 'name': 'Hindi'},
                        {'language': 'hmn', 'name': 'Hmong'},
                        {'language': 'hu', 'name': 'Hungarian'},
                        {'language': 'is', 'name': 'Icelandic'},
                        {'language': 'ig', 'name': 'Igbo'},
                        {'language': 'id', 'name': 'Indonesian'},
                        {'language': 'ga', 'name': 'Irish'},
                        {'language': 'it', 'name': 'Italian'},
                        {'language': 'ja', 'name': 'Japanese'},
                        {'language': 'jw', 'name': 'Javanese'},
                        {'language': 'kn', 'name': 'Kannada'},
                        {'language': 'kk', 'name': 'Kazakh'},
                        {'language': 'km', 'name': 'Khmer'},
                        {'language': 'rw', 'name': 'Kinyarwanda'},
                        {'language': 'ko', 'name': 'Korean'},
                        {'language': 'ku', 'name': 'Kurdish (Kurmanji)'},
                        {'language': 'ky', 'name': 'Kyrgyz'},
                        {'language': 'lo', 'name': 'Lao'},
                        {'language': 'la', 'name': 'Latin'},
                        {'language': 'lv', 'name': 'Latvian'},
                        {'language': 'lt', 'name': 'Lithuanian'},
                        {'language': 'lb', 'name': 'Luxembourgish'},
                        {'language': 'mk', 'name': 'Macedonian'},
                        {'language': 'mg', 'name': 'Malagasy'},
                        {'language': 'ms', 'name': 'Malay'},
                        {'language': 'ml', 'name': 'Malayalam'},
                        {'language': 'mt', 'name': 'Maltese'},
                        {'language': 'mi', 'name': 'Maori'},
                        {'language': 'mr', 'name': 'Marathi'},
                        {'language': 'mn', 'name': 'Mongolian'},
                        {'language': 'my', 'name': 'Myanmar (Burmese)'},
                        {'language': 'ne', 'name': 'Nepali'},
                        {'language': 'no', 'name': 'Norwegian'},
                        {'language': 'or', 'name': 'Odia (Oriya)'},
                        {'language': 'ps', 'name': 'Pashto'},
                        {'language': 'fa', 'name': 'Persian'},
                        {'language': 'pl', 'name': 'Polish'},
                        {'language': 'pt', 'name': 'Portuguese'},
                        {'language': 'pa', 'name': 'Punjabi'},
                        {'language': 'ro', 'name': 'Romanian'},
                        {'language': 'ru', 'name': 'Russian'},
                        {'language': 'sm', 'name': 'Samoan'},
                        {'language': 'gd', 'name': 'Scots Gaelic'},
                        {'language': 'sr', 'name': 'Serbian'},
                        {'language': 'st', 'name': 'Sesotho'},
                        {'language': 'sn', 'name': 'Shona'},
                        {'language': 'sd', 'name': 'Sindhi'},
                        {'language': 'si', 'name': 'Sinhala'},
                        {'language': 'sk', 'name': 'Slovak'},
                        {'language': 'sl', 'name': 'Slovenian'},
                        {'language': 'so', 'name': 'Somali'},
                        {'language': 'es', 'name': 'Spanish'},
                        {'language': 'su', 'name': 'Sundanese'},
                        {'language': 'sw', 'name': 'Swahili'},
                        {'language': 'sv', 'name': 'Swedish'},
                        {'language': 'tg', 'name': 'Tajik'},
                        {'language': 'ta', 'name': 'Tamil'},
                        {'language': 'tt', 'name': 'Tatar'},
                        {'language': 'te', 'name': 'Telugu'},
                        {'language': 'th', 'name': 'Thai'},
                        {'language': 'tr', 'name': 'Turkish'},
                        {'language': 'tk', 'name': 'Turkmen'},
                        {'language': 'uk', 'name': 'Ukrainian'},
                        {'language': 'ur', 'name': 'Urdu'},
                        {'language': 'ug', 'name': 'Uyghur'},
                        {'language': 'uz', 'name': 'Uzbek'},
                        {'language': 'vi', 'name': 'Vietnamese'},
                        {'language': 'cy', 'name': 'Welsh'},
                        {'language': 'xh', 'name': 'Xhosa'},
                        {'language': 'yi', 'name': 'Yiddish'},
                        {'language': 'yo', 'name': 'Yoruba'},
                        {'language': 'zu', 'name': 'Zulu'},
                        {'language': 'he', 'name': 'Hebrew'},
                        {'language': 'zh', 'name': 'Chinese (Simplified)'}]


