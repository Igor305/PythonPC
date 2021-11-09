import logging;
import os;
from datetime import datetime;

separator = "-------------------------------------------------" 

def createLogs():
    if not os.path.exists("logs"):
        os.mkdir("logs")

def checkDate():
    now = datetime.now()
    date_now = now.strftime("%m.%d.%Y")
    return(date_now)
    
def writeInfo(info):
    date_now = checkDate()
    logging.basicConfig(filename='logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.info(info)

def writeWarning(warning):
    date_now = checkDate()
    logging.basicConfig(filename='logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.warning(warning)

def writeError(error):
    date_now = checkDate()
    logging.basicConfig(filename='logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.error(error)

def writeResponseToLog(url,time):
    date_now = checkDate()
    logging.basicConfig(filename='logs/ %s.log' % date_now, format='%(asctime)s | %(levelname)s |\n%(message)s\n' + separator + separator + separator, level=logging.INFO)
    logging.info(url + '\nResponse time:%s' % time)