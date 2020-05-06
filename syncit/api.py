from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import json
import os
from syncit.delay_checker import DelayChecker
from syncit.constants import Constants
# from syncit.sync_checker import SyncChecker
from dotenv import load_dotenv
import logging
from logger_setup import setup_logging

load_dotenv()

setup_logging()
logger = logging.getLogger(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Constants.GOOGLE_APPLICATION_CREDENTIALS_PATH

app = Flask(__name__)

# On prod the nginx configuration takes care of the CORS
if(os.environ.get('Environment') == 'dev'):
    CORS(app)


# @app.route('/check_sync', methods=['POST'])
# def check_sync():
#     """
#     Route to check if buffers and subtitles are synced or not.

#     Request Params:
#         data (list): List of lists conatining [base64_buffer, subtitles] e.g: [[f3b5AAA, 'I went to eat'], [a93KKpr, 'I went to sleep']]

#     Returns:
#         Boolean: If synced or not.
#     """

#     logger.info('Checking sync.')
#     if(type(request.json) != dict):
#         print(type(request.json), len(request.json))
#         return Response(json.dumps({'error': 'Bad request.'}), 400)

#     try:
#         logger.debug('Request validated, getting json')
#         data = request.json['data']
#         extension = request.json['extension']
#         logger.debug('Recieved json, initating checker')
#         checker = SyncChecker(extension, data)
#         logger.debug('Check initiated, check is_synced')
#         is_synced = checker.check_is_synced()
#         return Response(json.dumps({'is_synced': is_synced}), 200)

#     except Exception as e:
#         logger.error(f'Error in check_sync. Error: {e}')
#         return Response(json.dumps({'error': 'Internal server error.'}), 500)


@app.route('/check_delay', methods=['POST'])
def check_delay():
    """
    Route to check the delay based on a timestamps.

    Request Params:
        file: FileStorage object with the video file.
        start: The start time of the video.
        end: The end time of the video.
        subtitles: The subtitles of this timestamps.
        extension: The extension of the video file.

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
        subtitles = request.form['subtitles']
        audio_language = request.form['audio_language']
        subtitles_language = request.form['subtitles_language']
        audio_file = request.files['file']
    except:
        return Response({'error': 'Bad Request'}, 400)

    try:
        dc = DelayChecker(audio_file, start, end, subtitles, audio_language, subtitles_language)
        delay = dc.check_delay_in_timespan()

        if(delay is None):
            return Response(json.dumps({}), 200)

        else:
            return Response(json.dumps({'delay': delay}), 200)
    except Exception as e:
        logger.error(f'Error in check_delay. Error: {e}')
        return Response(json.dumps({'error': 'Internal Server Error.'}), 500)


@app.errorhandler(404)
def page_not_found(e):
    return Response('404 not found', 404)
