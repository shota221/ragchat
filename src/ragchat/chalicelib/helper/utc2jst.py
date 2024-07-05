import datetime

def utc2jst(timestamp_utc):
    datetime_utc = datetime.datetime.strptime(timestamp_utc, "%Y-%m-%d %H:%M:%S")
    datetime_jst = datetime_utc.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
    timestamp_jst = datetime.datetime.strftime(datetime_jst, '%Y-%m-%d %H:%M:%S')
    return timestamp_jst