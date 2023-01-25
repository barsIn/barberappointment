import json
from datetime import datetime, date, time, timedelta
from jsonfilepy import jsonread, jsonwright
jsondict = jsonread()

def datToString(thisdate):
    if thisdate.day < 10:
        daystr = f'0{thisdate.day}'
    else:
        daystr = thisdate.day
    if thisdate.month < 10:
        monthstr = f'0{thisdate.month}'
    else:
        monthstr = thisdate.month
    thisdatestr = f'{daystr}.{monthstr}.{thisdate.year}'
    return thisdatestr


def hourStrtoTime(strhour):
    thour = time(int(strhour[0:2]), int(strhour[3:4]))
    return thour

def getUnworkTime(dict):
    unworkTime = []
    for hour in dict['unwork']['hours']:
        unworkTime.append(time(int(hour[0:2]), int(hour[3:4])))
    unworkTime.sort()
    return (unworkTime)

def getUnworkDays(dict):
    unworkDays = []
    for days in dict['unwork']['days']:
        day = date(int(days[6:]), int(days[3:5]), int(days[0:2]))
        unworkDays.append(day)
    return unworkDays


def getUnnworkWeekdays(dict):
    unworkWeekdays = []
    for weekday in dict['unwork']['weekdays']:
        unworkWeekdays.append(weekday)
    return unworkWeekdays



def checkWorkDay(day, dict):
    unnworkWeekdays = getUnnworkWeekdays(dict)
    unworkDays = getUnworkDays(dict)
    if day.weekday() in unnworkWeekdays:
        return False
    elif day in unworkDays:
        return False
    else:
        return True


def chekNextApoint(thisday, thistime,  jsondict):
    appoints = dict['appoint']
    daystr = datToString(thisday)
    dayappoint = appoints.get(daystr, False)
    workTime = hourStrtoTime(jsondict['unwork']['workhours'][0])
    if thistime < workTime:
        thistime = workTime
    else:
        thistime = time(thistime.hour+1, 00)
    if dayappoint:
        appointtimesstr = dayappoint.keys()
        appointtimes = []
        for item in appointtimesstr:
            item = hourStrtoTime(item)
            appointtimes.append(item)
        dinnerTimelist = jsondict['unwork']['dinerhours']
        for item in dinnerTimelist:
            appointtimes.append(hourStrtoTime(item))
        appointtimes.sort()
        for item in appointtimes:
            if thistime >= hourStrtoTime(jsondict['unwork']['workhours'][1]):
                return False
            if thistime < item:

                return thisday, thistime
            else:
                thistime = time(thistime.hour+1)
    else:
        return thisday, thistime

def nearestEntry(dict):
    nowtime = time(datetime.now().hour, datetime.now().minute)
    nowdate = date.today()
    unWorkHours = hourStrtoTime(jsondict['unwork']['workhours'][1])

    if nowtime > unWorkHours:
        nowdate = nowdate + timedelta(days=1)
        nowtime = time(0, 1)
    while(checkWorkDay(nowdate, dict) == False):
        nowdate = nowdate + timedelta(days=1)
        nowtime = time(0, 1)
    while(True):
        nextAppointnt = chekNextApoint(nowdate, nowtime, dict)
        if nextAppointnt:
            return nextAppointnt
        else:
            nowdate = nowdate + timedelta(days=1)
            nowtime = time(0, 1)



def getWorkingMode(dict):
    weekend = [
        'Понедельник',
        'Вторник',
        'Среда',
        'Четверг',
        'Пятница',
        'Суббота',
        'Воскресение'
    ]
    startHour = hourStrtoTime(dict['unwork']['workhours'][0])
    finishHour = hourStrtoTime(dict['unwork']['workhours'][1])
    weekdays = getUnnworkWeekdays(dict)
    weekdaystr = ''
    for item in weekdays:
        weekdaystr += weekend[item] + ', '
    dinnerTimelist = jsondict['unwork']['dinerhours']
    dinnerstr = ''
    for item in dinnerTimelist:
        dinnerstr += item + ', '
    print(f'Работаю с {startHour} до {finishHour}, выходные: {weekdaystr[0:-2]}, перерыв на обед {dinnerstr}')
    print(startHour, finishHour)


getWorkingMode(jsondict)


