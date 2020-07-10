from dotenv import load_dotenv
load_dotenv()
import os
import logging
from logger_setup import setup_logging
from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import json
from syncit.delay_checker import DelayChecker
from syncit.constants import Constants

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app) # Adds CORS header

@app.route('/check_delay', methods=['POST'])
def check_delay():
    """
    Route to check the delay based on a timestamps.

    Request Params:
        audio_file: FileStorage object with the video file.
        subtitles_file: FileStorage object with the complete subtitles.
        start: The start time of the video.
        end: The end time of the video.
        video_language: The lanaguage code of the video (and audio).
        subtitles_language: The language code of the subtitles.

    Response:
        If delay found:
            'subtitles': SubtitlesFile

        If delay not found:
            Empty dict.
    """
    
    logger.info('Checking delay.')
    try:
        start = int(request.form['start'])
        end = int(request.form['end'])
        audio_language = request.form['video_language']
        subtitles_language = request.form['subtitles_language']
        logger.debug(f'Languages: Subtitles - {subtitles_language}. Audio: {audio_language}.')
        subtitles_file = request.files['subtitles']
        audio_file = request.files['audio']
    except:
        return Response({'error': 'Bad Request'}, 400)

    try:
        dc = DelayChecker(audio_file, start, end, subtitles_file, audio_language, subtitles_language)
        delay = dc.check_delay()

        if(delay is None):
            return Response(json.dumps({}), 200)

        else:
            encoding = dc.sp.encoding
            return Response(json.dumps({'delay': delay, 'encoding': encoding}), 200)
    except Exception as e:
        logger.error(f'Error in check_delay. Error: {e}')
        return Response(json.dumps({'error': 'Internal Server Error.'}), 500)


@app.errorhandler(404)
def page_not_found(e):
    return Response('404 not found', 404)
