from syncit.tests.test_delay_checker import TestDelayChecker
import logging
from logger_setup import setup_logging


setup_logging()
logger = logging.getLogger(__name__)

if(__name__ == '__main__'):
    t = TestDelayChecker()
    t.setUp()
    t.test_get_occurences_for_grouped_sections()