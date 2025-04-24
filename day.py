from chinese_calendar import is_holiday, is_workday
from lolbot.common import config
import datetime
from lolbot.system import OS

def isValidTimeForRiotWin() -> bool:
    today = datetime.date.today()
    myconfig = config.load_config()
    if myconfig.riot and OS == 'Windows':
        res = is_holiday(today)
        if res:
            return True
        
        now = datetime.datetime.now()
        current_hour = now.hour
        print('current_hour' + str(current_hour))
        if current_hour <= 7 or current_hour >= 10:
            return True
        else:
            return False
    else:
        return True


def isValidTimeForRiotMac() -> bool:
    today = datetime.date.today()
    myconfig = config.load_config()
    if myconfig.riot and OS != 'Windows':
        res = is_holiday(today)
        if res:
            return True
        
        now = datetime.datetime.now()
        current_hour = now.hour
        if current_hour <= 7 or current_hour >= 19:
            return True
        else:
            return False
    else:
        return True