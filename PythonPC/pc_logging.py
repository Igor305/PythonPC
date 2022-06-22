from calendar import c
import logging;
import os;
from datetime import datetime;

separator = "-------------------------------------------------"
pathLog = "/home/pi/PricePython/logs"

def createLogs():
    if not os.path.exists(pathLog):
        os.mkdir(pathLog)

def _checkDate():
    date_now = datetime.now().strftime("%d.%m.%Y")
    return(date_now)

def _removeHandler():
    _removeOldDate()
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def _removeOldDate():
    today = datetime.today()
    os.chdir(pathLog)

    for root,directories,files in os.walk(pathLog):
        for name in files:
            t = os.stat(os.path.join(root, name))[8]
            filetime = datetime.fromtimestamp(t) - today

            if filetime.days <= -7:
                print(os.path.join(root, name), filetime.days)
                os.remove(os.path.join(root, name))

def writeInfo(info):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + '/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.info(info)

def writeWarning(warning):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + '/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.warning(warning)

def writeError(error):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + '/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.error(error)

def writeResponseToLog(url,time):
    date_now = _checkDate()
    _removeHandler()
    logging.basicConfig(filename = pathLog + '/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.info(url + '\nResponse time:%s' % time)