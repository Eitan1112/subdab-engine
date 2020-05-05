from syncit.tests.generate_report import check
import logging
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

if(__name__ == '__main__'):
    logger.debug('Starting!!')
    check()