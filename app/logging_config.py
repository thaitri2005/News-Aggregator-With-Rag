# app/logging_config.py
import logging
import logging.config
import os

def setup_logging():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,  # Keep existing loggers active
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'level': 'ERROR',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': os.path.join(os.getcwd(), 'app.log'),
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            },
        }
    }
    logging.config.dictConfig(logging_config)
