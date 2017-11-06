import time

# 整型时间戳转结构化时间

def int_struct(int_time):

    time_local = time.localtime(int_time)

    st = time.strftime("%Y-%m-%d %H:%M:%S", time_local)

    return st

# 结构化时间转为时间戳

def struct_int(struct_time):

    timeArray = time.strptime(struct_time, "%Y-%m-%d %H:%M:%S")

    timestamp = time.mktime(timeArray)

    return int(timestamp)

# 获取当天0点的时间戳

def today_zero():

    t = time.localtime(time.time())

    time_night = time.mktime(time.strptime(time.strftime('%Y-%m-%d 0:0:0', t), '%Y-%m-%d %H:%M:%S'))

    return time_night
