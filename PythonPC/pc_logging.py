import logging;
import os;
from datetime import datetime;

separator = "-------------------------------------------------"
pathLog = "/home/pi/PricePython/"

def createLogs():
    if not os.path.exists(pathLog + "logs"):
        os.mkdir(pathLog + "logs")

def _checkDate():
    now = datetime.now()
    date_now = now.strftime("%d.%m.%Y")
    return(date_now)

def _removeHandler():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def writeInfo(info):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + 'logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.info(info)

def writeWarning(warning):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + 'logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.warning(warning)

def writeError(error):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + 'logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.error(error)

def writeResponseToLog(url,time):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + 'logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.info(url + '\nResponse time:%s' % time)