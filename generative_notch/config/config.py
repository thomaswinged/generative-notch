import os.path
import logging
import yaml


__cfg = None


def get(path: str = None):
    global __cfg

    cfg_path = path if path else os.path.join(os.path.dirname(__file__), 'config.yml')
    # TODO Make dict of configs by path

    if not __cfg:
        with open(cfg_path) as file:
            logging.debug('Reading config file...')
            __cfg = yaml.safe_load(file)
            logging.debug('Done!')

    return __cfg
