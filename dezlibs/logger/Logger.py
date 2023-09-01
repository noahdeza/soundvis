import sys
import logging

LEVELS = {
    'debug':logging.DEBUG,
    'info':logging.INFO,
	'warning':logging.WARNING,
	'error':logging.ERROR,
	'critical':logging.CRITICAL,
}
FILE_NAME = 'app.log'
FILE_MODE = 'w'

DATE_FORMAT = f'%y-%m-%d %H:%M:%S'
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

def getLevel(lvl):
    return LEVELS.get(lvl) or logging.DEBUG

def get_filehandler(mode):
    fh = logging.FileHandler(
        filename=FILE_NAME,
        mode=mode
    )
    
    return fh

def get_streamhandler(lvl=None):
    sh = logging.StreamHandler()
    filename=FILE_NAME,
    filemode=FILE_MODE,
    datefmt=DATE_FORMAT,
    format=FORMAT,
    sh.setFormatter(fmt=logging.Formatter(fmt=FORMAT,datefmt=DATE_FORMAT,style='%'))
    sh.setLevel(getLevel(lvl))
    
    return sh

def createLogger(lvl=None, mode='w'):
    logger = logging.getLogger(__name__)
    logger.setLevel(lvl)
    logger.parent = False
    logger.addHandler(get_streamhandler(lvl))
    logger.addHandler(get_filehandler(mode))
    
    return logger
