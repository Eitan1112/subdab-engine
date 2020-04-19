from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
import json
from syncit.constants import Constants
from syncit.checker import Checker
import logging
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/check_sync', methods=['POST'])
@cross_origin()
def check_sync():
    """
    Route to check if buffers and subtitles are synced or not.
    
    Request Params:
        data (list): List of lists conatining [base64_buffer, subtitles] e.g: [[f3b5AAA, 'I went to eat'], [a93KKpr, 'I went to sleep']]

    Returns:
        Boolean: If synced or not.
    """

    if(type(request.json) != list or len(request.json) != Constants.SAMPLES_TO_CHECK):
        print(type(request.json), len(request.json))
        res = Response(json.dumps({ 'error': 'Bad request.'}), 400)
    else:
        # try:
        logger.debug('Request validated, getting json')
        data = request.json
        logger.debug('Recieved json, initating checker')
        checker = Checker(data)
        logger.debug('Check initiated, check is_synced')
        is_synced = checker.check_is_synced()
        logger.debug('Checked is synced', is_synced, ', Sending response')
        res = Response(json.dumps({ 'is_synced': is_synced }), 200)
        # except Exception as e:
        #     logger.warning(f'Error in check_sync. Error: {e}')
        #     res = Response(json.dumps({ 'error': 'Internal server error.'}), 500)

    return res



@app.route('/check_delay', methods=['POST'])
def check_delay():
    pass

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return Response('404 not found', 404)