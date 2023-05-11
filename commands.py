import json
from datetime import datetime, date, time, timedelta
from jsonfilepy import jsonread, jsonwright

def strDateToDate(thisdate):

    newDate = date(int(thisdate[6:]), int(thisdate[3:5]), int(thisdate[0:2]))
    if int(thisdate[6:]) < 2000:
        raise ValueError
    return newDate

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


def timeToString(thisTime):
    if thisTime.hour < 10:
        hourStr = f'0{thisTime.hour}'
    else:
        hourStr = f'{thisTime.hour}'
    if thisTime.minute < 10:
        minuteStr = f'0{thisTime.minute}'
    else:
        minuteStr = f'{thisTime.minute}'
    thisTimeStr = f'{hourStr}:{minuteStr}'
    return thisTimeStr


def hourStrtoTime(strhour):
    thour = time(int(strhour[0:2]), int(strhour[3:5]))
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

def getDinnerTime(dict):
    dinnerTimelistStr = dict['unwork']['dinerhours']
    dinerTime = []
    if len(dinnerTimelistStr) == 0:
        return dinerTime
    startTime, finishTime = hourStrtoTime(dict['unwork']['dinerhours'][0]), hourStrtoTime(
        dict['unwork']['dinerhours'][1])
    dinerDelta = finishTime.hour - startTime.hour
    if dinerDelta == 1:
        dinerTime = [startTime]
    else:
        for t in range(dinerDelta):
            dinerTime.append(startTime.hour+t)
    return dinerTime


def checkWorkDay(day):
    jsondict = jsonread()
    unnworkWeekdays = getUnnworkWeekdays(jsondict)
    unworkDays = getUnworkDays(jsondict)
    if day.weekday() in unnworkWeekdays:
        return False
    elif day in unworkDays:
        return False
    else:
        return True

def checkClient(telephone, jsondict):
    clients = jsondict['client']
    client = clients.get(telephone, False)
    if client:
        return [telephone, client[0], client[1]]
    else:
        return False


def addClient(telephone, name, tac):
    jsondict = jsonread()
    jsondict['client'][telephone] = [name, tac]
    jsonwright(jsondict)


def chekNextApoint(thisday, thistime):
    jsondict = jsonread()
    appoints = jsondict['appoint']
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
                if len(getDinnerTime(jsondict)) == 0:
                    return thisday, thistime
                else:
                    for t in getDinnerTime(jsondict):
                        if thistime.hour == t:
                            thistime = time(thistime.hour+1)
                return thisday, thistime
            else:
                thistime = time(thistime.hour+1)
    else:
        if len(getDinnerTime(jsondict)) == 0:
            return thisday, thistime
        else:
            for t in getDinnerTime(jsondict):
                if thistime.hour == t:
                    thistime = time(thistime.hour+1)
        return thisday, thistime

def nearestEntry():
    jsondict = jsonread()
    nowtime = time(datetime.now().hour, datetime.now().minute)
    nowdate = date.today()
    unWorkHours = hourStrtoTime(jsondict['unwork']['workhours'][1])

    if nowtime > unWorkHours:
        nowdate = nowdate + timedelta(days=1)
        nowtime = time(0, 1)
    while(checkWorkDay(nowdate) == False):
        nowdate = nowdate + timedelta(days=1)
        nowtime = time(0, 1)
    while(True):
        nextAppointnt = chekNextApoint(nowdate, nowtime)
        if nextAppointnt:
            result = f'следующая запись на {nextAppointnt[0].strftime("%d.%m.%Y")} в {nextAppointnt[1].strftime("%H:%M")}'
            return result
        else:
            nowdate = nowdate + timedelta(days=1)
            nowtime = time(0, 1)


def getWorkingMode():
    dict = jsonread()
    WEEKEND = [
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
        weekdaystr += WEEKEND[item] + ', '
    dinnerTimelist = dict['unwork']['dinerhours']
    if len(dinnerTimelist) == 0:
        result = f'Работаю с {startHour.strftime("%H:%M")} до {finishHour.strftime("%H:%M")}, выходные: {weekdaystr[0:-2]}'
    else:
        result = f'Работаю с {startHour.strftime("%H:%M")} до {finishHour.strftime("%H:%M")}, выходные: {weekdaystr[0:-2]}, перерыв на обед c {dinnerTimelist[0]} до {dinnerTimelist[1]}'
    return result


def makeAppoint(name, telephone, tac, thisDate, thisTime, barbtype):
    jsondict = jsonread()
    if not(checkClient(telephone, jsondict)):
        addClient(telephone, name, tac)
    if jsondict['appoint'].get(datToString(thisDate), False):
        jsondict['appoint'][datToString(thisDate)][timeToString(thisTime)] = [
            tac,
            telephone,
            barbtype
        ]
    else:
        jsondict['appoint'][datToString(thisDate)] = {timeToString(thisTime): [
            tac,
            telephone,
            barbtype
        ]
        }

    jsonwright(jsondict)

def getUnbusyTimes(askedDate):
    jsondict = jsonread()
    try:
        strDateToDate(askedDate)
    except:
        return 'Неверный формат даты'
    if not checkWorkDay(strDateToDate(askedDate)):
        return 'В этот день выходной'
    dinnerTime = getDinnerTime(jsondict)
    strtTime = hourStrtoTime(jsondict['unwork']['workhours'][0])
    finishTime = hourStrtoTime(jsondict['unwork']['workhours'][1])
    timeList = []
    resultTimelist = []
    busylist = []
    for item in range(strtTime.hour, finishTime.hour):
        timeList.append(time(item, 0))
    if jsondict['appoint'].get(askedDate, False):
        busyStrlist = list(jsondict['appoint'][askedDate].keys())
        for t in busyStrlist:
            busylist.append(hourStrtoTime(t))
    busylist = busylist + dinnerTime
    for t in timeList:
        if t not in busylist:
            resultTimelist.append(t)
    return resultTimelist

def deleteAppoint(telephone, tac):
    jsondict = jsonread()
    appdates = jsondict['appoint'].keys()
    accapoint = False
    for appointday in appdates:
        times = jsondict['appoint'][appointday].keys()
        for thistime in times:
            if jsondict['appoint'][appointday][thistime][0] == tac or jsondict['appoint'][appointday][thistime][1] == telephone:
                accapoint = [appointday, thistime]
    if accapoint:
        jsondict['appoint'][accapoint[0]].pop(accapoint[1])
    else:
        return 'Нет записей'
    jsonwright(jsondict)

deleteAppoint('+79233211713', '@tac')
def checkAppoint(telephone):
    jsondict = jsonread()
    appdates = jsondict['appoint'].keys()
    accapoint = []
    for appointday in appdates:
        times = jsondict['appoint'][appointday].keys()
        for thistime in times:
            if jsondict['appoint'][appointday][thistime][1] == telephone:
                accapoint = [appointday, thistime]
    if len(accapoint) != 2:
        return 'Нет записей'
    else:
        return f'У Вас есть запись на {accapoint[0]} в {accapoint[1]}'

def weekedsToNumbers(weekeds):
    WEEKEND = {
        'Понедельник': 0,
        'Вторник': 1,
        'Среда': 2,
        'Четверг': 3,
        'Пятница': 4,
        'Суббота': 5,
        'Воскресение': 6
    }
    weekNumbers = []
    weekeds = weekeds.replace(' ', '')
    weekedsList = weekeds.split(',')
    for i in range(len(weekedsList)):
        weekedsList[i] = weekedsList[i].title()
    for it in weekedsList:
        weekNumbers.append(WEEKEND.get(it, False))
    return weekNumbers

# admin functions
def makeWeekend(weekendsStr):
    jsondict = jsonread()
    WEEKEND = {
        'Понедельник': 0,
        'Вторник': 1,
        'Среда': 2,
        'Четверг': 3,
        'Пятница': 4,
        'Суббота': 5,
        'Воскресение': 6
    }
    answer = ''
    if weekendsStr == 'Без выходных':
        jsondict['unwork']['weekdays'] = []
        answer = 'Уcтановлен режим работы без выходных'
    else:
        if weekendsStr in WEEKEND.keys():
            jsondict['unwork']['weekdays'] = []
            jsondict['unwork']['weekdays'].append(WEEKEND[weekendsStr])
            answer = f'{weekendsStr} успешно добавлен к выходным'
        else:
            answer = 'Ошибка в слове. Не пиши сам, тыкай кнопки'
    jsonwright(jsondict)
    return answer


def addUnworckDay(unworckDay):
    answer = ''
    try:
        strDateToDate(unworckDay)
        jsondict = jsonread()
        jsondict['unwork']['days'].append(unworckDay)
        answer = f'{unworckDay} успешно добавлен к нерабочим дням.'
        jsonwright(jsondict)
    except ValueError:
        answer = 'Неверный формат даты.'
    return answer


def setupWorkTime(workTimeStart, workTimeFinish):
    answer = ''
    try:
        hourStrtoTime(workTimeStart)
        hourStrtoTime(workTimeFinish)
        if (int(workTimeStart[0:2]) > int(workTimeFinish[0:2])):
            return 'Время окончания работы должно быть позже времени начала.'

        jsondict = jsonread()
        workTimelist = [workTimeStart, workTimeFinish]
        jsondict['unwork']['workhours'] = workTimelist.copy()
        answer = f'режим работы установлен с {workTimeStart} до {workTimeFinish}.'
        jsonwright(jsondict)
    except ValueError:
        answer = 'Неверный формат времени, попробуй еще раз.'
    return answer


def getAppointstime(dayveiw):
    answer = ''
    try:
        strDateToDate(dayveiw)
    except ValueError:
        return 'Неверный формат времени, попробуй еще раз.'
    jsondict = jsonread()
    if jsondict['appoint'].get(dayveiw, False):
        appoints = list(jsondict['appoint'][dayveiw].keys())
        return appoints
    else:
        return 'Нет записей'


def todayAppoiintsview():
    jsondict = jsonread()
    thisDay = datToString(date.today())
    appointsTime = getAppointstime(thisDay)
    if appointsTime == 'Нет записей':
        return 'Нет записей'
    else:
        appointsTime = list(map(hourStrtoTime, appointsTime))
        print(appointsTime)
        result = 'На сегодня еще записи:\n'
        for i in appointsTime:
            if datetime.now().hour < i.hour:
                result += f'{timeToString(i)} {jsondict["appoint"][thisDay][timeToString(i)][0]}, телефон {jsondict["appoint"][thisDay][timeToString(i)][1]}\n'
    return result


def dateAppointsview(dateview):
    jsondict = jsonread()
    appointsTime = getAppointstime(dateview)
    if appointsTime == 'Нет записей':
        return 'Нет записей'
    else:
        appointsTime = list(map(hourStrtoTime, appointsTime))
        result = f'На {dateview} есть записи:\n'
        for i in appointsTime:
            result += f'{timeToString(i)} {jsondict["appoint"][dateview][timeToString(i)][0]}, телефон {jsondict["appoint"][dateview][timeToString(i)][1]}\n'
    return result


# jsondict = jsonread()
# print(dateAppointsview('02.02.2023'))

# makeAppoint('Viktoria', '+79233418990', '@vov', date(2023, 2, 2), time(11, 15), 'complex')
# print(jsonread()['appoint'])
# checkClient('Igor', jsonread())thistimes = time(10, 15)
# thistimes.minute

