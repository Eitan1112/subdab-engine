from flask import Flask, request, Response
import json
from syncit.checker import Checker
import logging
from logger_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/check_sync', methods=['POST'])
def check_sync():
    """
    Route to check if buffers and subtitles are synced or not.
    
    Request Params:
        data (list): List of lists conatining [base64_buffer, subtitles] e.g: [[f3b5AAA, 'I went to eat'], [a93KKpr, 'I went to sleep']]

    Returns:
        Boolean: If synced or not.
    """

    if(not request.form['data']):
        res = Response(json.dumps({ 'error': 'Bad request. Expected data param in request.'}), 401)
    else:
        try:
            data = request.form['data']
            checker = Checker(data)
            is_synced = checker.check_is_synced()
            res = Response(json.dumps({ 'is_synced': is_synced }), 200)
        except Exception as e:
            logger.warning(f'Error in check_sync. Error: {e}')
            res = Response(json.dumps({ 'error': 'Internal server error.'}), 500)

    return res



@app.route('/check_delay', methods=['POST'])
def check_delay():
    pass