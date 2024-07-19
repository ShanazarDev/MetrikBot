from loguru import logger
from headbot_data import send_stat

class LogFolderPath:
    path = 'logs/'

def info_filter(record):
    return record["level"].name == "INFO" or record["level"].name == "SUCCESS"


def error_filter(record):
    try:
        send_stat('error')
    except Exception:
        pass

    return record["level"].name == "ERROR" and not "traceback" in record["extra"]


logger.add(LogFolderPath.path + 'info.log', filter=info_filter, format="{time:MMMM D, YYYY > HH:mm:SS.SSSS} | {level} | {message}",
           level="INFO",
           rotation="1 day")
logger.add(LogFolderPath.path + 'error.log', filter=error_filter, format="{time:MMMM D, YYYY > HH:mm:SS.SSSS} | {level} | {message}",
           level="ERROR",
           rotation="1 day")
