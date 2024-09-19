from datetime import datetime, timedelta

TRADE_MILIS = 19800000 # number of miliseconds from 9h to 14h30
FULL_DAY_MILIS = 86280000 # number of miliseconds from 0h01 to 23h59
NON_TRADE_MILIS = FULL_DAY_MILIS - TRADE_MILIS

def calculate_distance_milis(datetime, start_time, is_subtract_trade_time=False):
        if type(datetime) is str:
            datetime = make_date_from_string(datetime)
            
        if type(start_time) is str:
            start_time = make_date_from_string(start_time)
        num_days = (datetime - start_time).days
        if is_subtract_trade_time:
            return (datetime - start_time).total_seconds() * 1000.0 - (TRADE_MILIS*num_days)
        return (datetime - start_time).total_seconds() * 1000.0

def make_date_to_tickersymbol(date_obj):
    if type(date_obj) is str:
        date_obj = make_date_from_string(date_obj)

    maturity_date = get_maturity_date(date_obj)
    
    year = date_obj.strftime("%y")
    month = date_obj.strftime("%m")

    if date_obj > maturity_date:
        month = str(int(month) + 1)
        # format month is two digit, examples 01, 02, 03 ,04 ,05
        month = month.zfill(2)
        if month == "13":
            month = "01"
            year = str(int(year) + 1)

    return f"VN30F{year}{month}"

def make_date_from_string(input_date):
    if type(input_date) is str:
        try:
            if "," in input_date:
                input_date = input_date.replace(",", ".")
            if "." in input_date:
                date_obj = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S.%f")
            elif ":" in input_date:
                date_obj = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
            else:
                date_obj = datetime.strptime(input_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please provide a date in the format '%Y-%m-%d' or '%Y-%m-%d %H:%M:%S.%f'. ")
    else:
        date_obj = input_date
    return date_obj

def check_two_stringtime_greater_thresh(time1, time2, thresh):
    if len(time1) == 0 or len(time2) == 0:
        print("Invalid time format", "time1:", time1, "time2:", time2)
        return False
    date_obj1 = make_date_from_string(time1)
    date_obj2 = make_date_from_string(time2)
    return (date_obj2 - date_obj1).seconds > thresh

def check_stringtime_greater_closetime(datetime, closetimealgo):
    datetime = make_date_from_string(datetime)
    string_closetime = datetime.strftime("%Y-%m-%d") + " " + closetimealgo
    datetime_closing = make_date_from_string(string_closetime)
    return datetime.time() > datetime_closing.time()

def check_stringtime_less_starttime(date1, date2):
    date_obj1 = make_date_from_string(date1)
    string_date2 = date_obj1.strftime("%Y-%m-%d") + " " + date2
    date_obj2 = make_date_from_string(string_date2)
    return date_obj1.time() < date_obj2.time()

def check_two_string_is_same_day(date1, date2):
    date_obj1 = make_date_from_string(date1)
    date_obj2 = make_date_from_string(date2)
    return date_obj1.date() == date_obj2.date()


def is_same_week_as_third_thursday(input_date):
    date_obj = make_date_from_string(input_date)
    # Find the first day of the month and the number of days in the month
    first_day_of_month = date_obj.replace(day=1)
    first_thursday = first_day_of_month + timedelta(days=((3-first_day_of_month.weekday()) % 7))
    third_thursday = first_thursday + timedelta(days=14)
    start_of_week = third_thursday - timedelta(days=third_thursday.weekday())
    
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week <= date_obj <= end_of_week

def get_maturity_date(date):
    """Get the third thursday of the month of the given date
    Args:
        date (datetime): _description_

    Returns:
        datetime: _description_
    """
    if type(date) is str:
        date = make_date_from_string(date)
    month = date.strftime("%m")
    year = date.strftime("%y")
    first_day_of_month = datetime.strptime(f"20{year}-{month}-01", "%Y-%m-%d")
    first_thursday = first_day_of_month + timedelta(days=((3-first_day_of_month.weekday()) % 7))
    third_thursday = first_thursday + timedelta(days=14)
    return third_thursday

def get_maturity_date_from_symbol(tickerymbol):
    month = tickerymbol[-2:]
    year = tickerymbol[-4:-2]
    first_day_of_month = datetime.strptime(f"20{year}-{month}-01", "%Y-%m-%d")
    first_thursday = first_day_of_month + timedelta(days=((3-first_day_of_month.weekday()) % 7))
    third_thursday = first_thursday + timedelta(days=14)
    return third_thursday.strftime("%Y-%m-%d")


def get_num_days_to_maturity(tickerymbol, date):
    maturity_date = get_maturity_date_from_symbol(tickerymbol)
    date_obj = make_date_from_string(date)
    maturity_date_obj = datetime.strptime(maturity_date, "%Y-%m-%d")
    return (maturity_date_obj - date_obj).days + 1


def auto_convert_string_to_datetime(obj):
    if type(obj) is str:
        return make_date_from_string(obj)
    return obj