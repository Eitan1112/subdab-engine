import os
import json
import logging.config
import logging

def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Setup logging configuration.
    """

    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('chardet').setLevel(logging.WARNING)
    path = default_path
    value = os.getenv(env_key, None)
    if(value):
        path = value
    if(os.path.exists(path)):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)