import os


class Constants():
    DELAY_RADIUS = 22  # Seconds
    ONE_WORD_AUDIO_TIME = 1  # How much seconds it takes to say one word (max)

    # In seconds, have to be synced with frontend.
    DELAY_CHECKER_SECTIONS_TIME = 300
    # After verifing X delays, send a response without delay to recieve new timestamp.
    MAXIMUM_DELAYS_TO_VERIFY = 15

    VERIFY_DELAY_SAMPLES_TO_CHECK = 15
    VERIFY_DELAY_SAMPLES_TO_PASS = 6
    VERIFY_DELAY_TRANSLATED_SAMPLES_TO_PASS = 6

    AUDIO_LANGUAGES = [
        {'code': 'en', 'pocketsphinx_code': 'en-US'},
        {'code': 'it', 'pocketsphinx_code': 'it-IT'},
        {'code': 'fr', 'pocketsphinx_code': 'fr-FR'},
        {'code': 'es', 'pocketsphinx_code': 'es-ES'},
        {'code': 'mx', 'pocketsphinx_code': 'es-MX'},
        {'code': 'de', 'pocketsphinx_code': 'de-DE'},
        {'code': 'el', 'pocketsphinx_code': 'el-GR'},
        {'code': 'hi', 'pocketsphinx_code': 'hi-HI'},
        {'code': 'kz', 'pocketsphinx_code': 'kz-KZ'},
        {'code': 'nl', 'pocketsphinx_code': 'nl-NL'},
        {'code': 'ru', 'pocketsphinx_code': 'ru-RU'},
        {'code': 'zh', 'pocketsphinx_code': 'zh-CN'},
    ]

    RECIEVED_AUDIO_FILE_EXTENSION = 'm4a'
    DESIRED_AUDIO_FILE_EXTENSION = 'wav'

    SAMPLES_FOLDER = os.path.join('syncit', 'tests', 'samples')

    # Section time for the filter hot words method
    FILTER_HOT_WORDS_SECTION = 35
    FILTER_HOT_WORDS_ADD_TO_END = 10

    # Beyond 45 occurences in the above timestamp, the hot word is removed
    FILTER_HOT_WORDS_MAXIMUM_OCCURENCES = 45

    # Grouped sections time
    DIVIDED_SECTIONS_TIME = 4

    RETRIES_AFTER_API_ERROR = 4
    
    MAX_OCCURENCES_IN_ONE_SECTION = 2
    MAX_OCCURENCES_FOR_ONE_WORD = 2
    TRIM_SECTION_STEP = 0.2
    REQUEST_TIMEOUT = 8

    VERIFY_TRIMMED_WORD_RADIUS = 0.4

    GOOGLE_AUTH_FILENAME = 'google_auth.json'

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
