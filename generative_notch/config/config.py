import os.path
import logging
import yaml


__cfg = None


def get():
    global __cfg

    if not __cfg:
        with open(os.path.join(os.path.dirname(__file__), 'config.yml')) as file:
            logging.debug('Reading config file...')
            __cfg = yaml.safe_load(file)

    return __cfg
