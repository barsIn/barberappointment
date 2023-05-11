from dotenv import load_dotenv
from datetime import datetime, date, time
import os
import telebot
from telebot import types
from commands import getWorkingMode, nearestEntry, getUnbusyTimes, hourStrtoTime, makeAppoint, strDateToDate, deleteAppoint, checkAppoint
from commands import setupWorkTime, makeWeekend, addUnworckDay, getAppointstime, datToString, todayAppoiintsview, dateAppointsview
load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))
# bot = telebot.TeleBot('5393108567:AAHrrNpHv8ab0sH82OUaRNVzWrIAGirKhyA')

USERS = [
    588726946,
    501830992,
    884307774,
    353034106
]
appoint_dict = {}
worktimelist = []


class Appoint:
    def __init__(self, day, tac):
        self.day = day
        self.username = None
        self.telephone = None
        self.tac = tac
        self.time = None
        self.barbertype = None

class Worktime:
    def __init__(self, start):
        self.start = start
        self.finish = None

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
    admin = types.KeyboardButton('Я админ')
    user = types.KeyboardButton('Я просто записаться')
    keyboard.add(admin, user)
    bot.send_message(message.chat.id, 'Ты админ или записаться?', reply_markup=keyboard)

@bot.message_handler(commands=['admin'])
@bot.message_handler(func=lambda message: message.text == 'Я админ')
def admin(message):
    text = 'Вы можете:\n' \
           'Установить рабочее время\n' \
           'Установить выходные дни\n' \
           'Установить обеденное время\n' \
           'Посмотреть ближайшую запись\n' \
           'Проверить сегодняшние записи\n' \
           'Посмотреть записи на дату\n' \
           'Записать человека'
    if message.from_user.id in USERS:
        worktimelist = []
        kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        setup_work_time = types.KeyboardButton('Установить рабочее время')
        set_weekend = types.KeyboardButton('Установить выходные дни')
        set_dinner_time = types.KeyboardButton('Установить обеденное время')
        see_nearles_appint = types.KeyboardButton('Посмотреть ближайшую запись')
        see_today_appoint = types.KeyboardButton('Проверить сегодняшние записи')
        see_appoint_ondate = types.KeyboardButton('Посмотреть записи на дату')
        admin_make_appoint = types.KeyboardButton('Записать человека')
        kb.add(setup_work_time, set_weekend, set_dinner_time, see_nearles_appint, see_today_appoint, see_appoint_ondate, admin_make_appoint)
        bot.send_message(message.chat.id, text, reply_markup=kb)
    else:
        bot.send_message(message.chat.id, 'Проваливай самозванец')

@bot.message_handler(commands=['setup_work_time'])
@bot.message_handler(func=lambda message: message.text == 'Установить рабочее время')
def setup_work_time(message):
    worktimelist = []
    dinnertimelist = []
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    back = types.KeyboardButton('Назад')
    kb.add(back)
    text = 'Введи время начала рабочего дня в формате ЧЧ:ММ'
    msg = bot.reply_to(message, text, reply_markup=kb)
    bot.register_next_step_handler(msg, start_work)

def start_work(message):
    if message.text == 'Назад':
        admin(message)
        # msg = bot.reply_to(message, text)
        # bot.register_next_step_handler(msg, admin)
    else:
        try:
            hourStrtoTime(message.text)
            message_text = message.text.replace('.', ':')
            worktime = Worktime(message_text)
            worktimelist.append(worktime)
            msg = bot.reply_to(message, 'Введи время окончания рабочего дня')
            bot.register_next_step_handler(msg, finish_work)
        except ValueError:
            text = 'Неверный формат времени, попробуй еще раз в формате ЧЧ:ММ'
            msg = bot.reply_to(message, text)
            bot.register_next_step_handler(msg, start_work)


def finish_work(message):
    try:
        hourStrtoTime(message.text)
    except ValueError:
        text = 'Неверный формат времени, попробуй еще раз в формате ЧЧ:ММ'
        msg = bot.reply_to(message, text)
        bot.register_next_step_handler(msg, finish_work)
    message_text = message.text.replace('.', ':')
    worktime = worktimelist[0]
    worktime.finish = message_text
    worktimelist[0] = worktime
    result = setupWorkTime(worktime.start, worktime.finish)
    if result == 'Время окончания работы должно быть позже времени начала.':
        msg = bot.reply_to(message, result)
        bot.register_next_step_handler(msg, setup_work_time)
    else:
        msg = bot.reply_to(message, result)
        bot.register_next_step_handler(msg, admin)

@bot.message_handler(commands=['setup_weekends'])
@bot.message_handler(func=lambda message: message.text == 'Установить выходные дни')
def setup_weekends(message):
    kb = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    weekend_days = types.KeyboardButton('Установить выходные дни недели')
    unwok_days = types.KeyboardButton('Установить дополнительные дни отдыха')
    kb.add(weekend_days, unwok_days)
    text = 'Установить выходные дни недели или просто конкретные дни'
    bot.send_message(message.chat.id, text, reply_markup=kb)

bot.message_handler(commands=['setup_weekends_days'])
@bot.message_handler(func=lambda message: message.text == 'Установить выходные дни недели')
def setup_weekends_days(message):
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    mononday = types.KeyboardButton('Понедельник')
    tuesday = types.KeyboardButton('Вторник')
    wednesday = types.KeyboardButton('Среда')
    thursday = types.KeyboardButton('Четверг')
    friday = types.KeyboardButton('Пятница')
    saturday = types.KeyboardButton('Суббота')
    sunday = types.KeyboardButton('Воскресение')
    without = types.KeyboardButton('Без выходных')
    kb.add(mononday, tuesday, wednesday, thursday, friday, saturday, sunday, without)
    text = 'Выбери день, который необходимо сделать выходным, либо укажи режим "Без выходных"'
    msg = bot.send_message(message.chat.id, text, reply_markup=kb)
    bot.register_next_step_handler(msg, make_weekend_day)

def make_weekend_day(message):
    text = makeWeekend(message.text)
    bot.reply_to(message, text)
    admin(message)

bot.message_handler(commands=['setup_unwork_days'])
@bot.message_handler(func=lambda message: message.text == 'Установить дополнительные дни отдыха')
def setup_unwork_days(message):
    text = 'Введи дату в формате дд.мм.гггг'
    msg = bot.reply_to(message, text)
    bot.register_next_step_handler(msg, make_unwork)

def make_unwork(message):
    text = addUnworckDay(message.text)
    bot.reply_to(message, text)
    admin(message)


@bot.message_handler(commands=['setup_dinner_time'])
@bot.message_handler(func=lambda message: message.text == 'Установить обеденное время')
def setup_dinner_time(message):
    text = 'Ты сказал, что работаешь без обеда'
    bot.reply_to(message, text)
    admin(message)

@bot.message_handler(commands=['my_near_appoint'])
@bot.message_handler(func=lambda message: message.text == 'Посмотреть ближайшую запись')
def my_near_appoint(message):
    this_day = date.today()
    this_dayStr = datToString(this_day)
    text = getAppointstime(this_dayStr)
    bot.reply_to(message, text)


@bot.message_handler(commands=['today_appoint'])
@bot.message_handler(func=lambda message: message.text == 'Проверить сегодняшние записи')
def my_near_appoint(message):
    text = todayAppoiintsview()
    bot.reply_to(message, text)
@bot.message_handler(commands=['user'])
@bot.message_handler(func=lambda message: message.text == 'Я просто записаться')
@bot.message_handler(func=lambda message: message.text == 'Записаться')
def user_gritings(message):
    text = 'Вы можете:\n' \
           'Узнать режим работы\n' \
           'Посмотреть ближайшую запись\n' \
           'Посмотреть доступное время на конкретную дату\n' \
           'Осуществить запись\n' \
           'Отменить существующую запись\n' \
           'Проверить текущую запись'
    print(message.from_user.id)
    print(message.from_user.username)
    kb = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    ask_time = types.KeyboardButton('Узнать режим работы')
    next_appoint = types.KeyboardButton('Посмотреть ближайшую запись')
    availability = types.KeyboardButton('Посмотреть доступное время на конкретную дату')
    make_appoint = types.KeyboardButton('Осуществить запись')
    cancel_appoint = types.KeyboardButton('Отменить существующую апись')
    check_appoint = types.KeyboardButton('Проверить текущую запись')
    kb.add(ask_time, next_appoint)
    kb.add(availability)
    kb.add(make_appoint, cancel_appoint)
    kb.add(check_appoint)
    bot.send_message(message.chat.id, text, reply_markup=kb)


@bot.message_handler(commands=['ask_time'])
@bot.message_handler(func=lambda message: message.text == 'Узнать режим работы')
def ask_time(message):
    text = getWorkingMode()
    bot.send_message(message.chat.id, text)
    user_gritings(message)

@bot.message_handler(commands=['next_appoint'])
@bot.message_handler(func=lambda message: message.text == 'Посмотреть ближайшую запись')
def next_appoint(message):
    text = nearestEntry()
    bot.send_message(message.chat.id, text)
    user_gritings(message)

@bot.message_handler(commands=['availability'])
@bot.message_handler(func=lambda message: message.text == 'Посмотреть доступное время на конкретную дату')
def check_appoint(message):
    text = 'Введи требуемую дату в формате дд.мм.гггг'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, enter_date)

def enter_date(message):
    answer = getUnbusyTimes(message.text)
    if answer == 'Неверный формат даты':
        text = 'Попробуй еще раз неверный формат даты'
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, enter_date)
    elif answer == 'В этот день выходной':
        text = 'В этот день выходной, попробовать другую дату'
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, enter_date)
    else:
        text = 'Есть свободная запись:\n'
        for i in answer:
            text += f'{i.strftime("%H:%M")}\n'
        bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['check_appoint'])
@bot.message_handler(func=lambda message: message.text == 'Проверить текущую запись')
def check_appoint(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    bt = types.KeyboardButton(text='Передать телефон', request_contact=True)
    keyboard.add(bt)
    msg = bot.reply_to(message, "Сообщите телефон для проверки записи", reply_markup=keyboard)
    bot.register_next_step_handler(msg, chek_appoint)


def chek_appoint(message):
    telephone = message.contact.phone_number
    text = checkAppoint(telephone)
    bot.send_message(message.chat.id, text)
    user_gritings(message)

@bot.message_handler(commands=['make_appoint'])
@bot.message_handler(func=lambda message: message.text == 'Осуществить запись')
def make_appoint(message):
    text = 'Введи требуемую дату для записи в формате дд.мм.гггг'
    msg = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(msg, enter_appoint_date)

def enter_appoint_date(message):
    answer = getUnbusyTimes(message.text)
    if answer == 'Неверный формат даты':
        text = 'Попробуй еще раз неверный формат даты'
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, enter_appoint_date)
    elif answer == 'В этот день выходной':
        text = 'В этот день выходной, попробовать другую дату'
        msg = bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(msg, enter_appoint_date)
    else:
        chat_id = message.chat.id
        if appoint_dict.get(chat_id, False):
            appoint_dict.pop(chat_id)
        date = message.text
        tac = message.from_user.username
        appoint = Appoint(day=date, tac=tac)
        appoint_dict[chat_id] = appoint
        if message.from_user.first_name:
            appoint.user = message.from_user.first_name
            appoint_dict[chat_id] = appoint
        msg = bot.reply_to(message, 'На какое время осуществить запись?')
        bot.register_next_step_handler(msg, time_appoint)

def time_appoint(message):
    try:
        hourStrtoTime(message.text)
        chat_id = message.chat.id
        times = getUnbusyTimes(appoint_dict[chat_id].day)
        strtimes = []
        answer = ''
        message_text = message.text.replace('.', ':')
        for i in times:
            strtimes.append(i.strftime("%H:%M"))
            answer += f'{i.strftime("%H:%M")}\n'
        if not message_text in strtimes:
            msg = bot.reply_to(message, f"Нет записи на это время\n Есть запись на\n {answer}")
            bot.register_next_step_handler(msg, time_appoint)
        else:
            appoint_dict[chat_id].time = message_text
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=3, resize_keyboard=True)
            hear = types.KeyboardButton('Только стрижка')
            beard = types.KeyboardButton('Борода')
            complex = types.KeyboardButton('Стрижка и борода')
            keyboard.add(hear, beard, complex)
            msg = bot.send_message(message.chat.id, 'Что будем стричь?', reply_markup=keyboard)
            bot.register_next_step_handler(msg, ask_telephone)
    except ValueError:
        text = 'Неверный формат времени, попробуй еще раз в формате ЧЧ:ММ'
        msg = bot.reply_to(message, text)
        bot.register_next_step_handler(msg, time_appoint)


def ask_telephone(message):
    barbertypes = {
        'Только стрижка': 'hear',
        'Борода': 'beard',
        'Стрижка и борода': 'complex'
    }
    chat_id = message.chat.id
    appoint = appoint_dict[chat_id]
    appoint.barbertype = barbertypes[message.text]
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    bt = types.KeyboardButton(text='Передать телефон', request_contact=True)
    keyboard.add(bt)
    msg = bot.reply_to(message, "Остался телефон и запись будет готова", reply_markup=keyboard)
    bot.register_next_step_handler(msg, new_appoint)


def new_appoint(message):
    telephone = message.contact.phone_number
    chat_id = message.chat.id
    appoint = appoint_dict[chat_id]
    appoint.telephone = telephone
    makeAppoint(appoint.username, appoint.telephone, appoint.tac, strDateToDate(appoint.day), hourStrtoTime(appoint.time), appoint.barbertype)
    text = f'Запись успешно осуществлена на {appoint.day} в {appoint.time}'
    bot.reply_to(message, text)
    user_gritings(message)

@bot.message_handler(commands=['cancel_appoint'])
@bot.message_handler(func=lambda message: message.text == 'Отменить существующую апись')
def cancel_appoint(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    bt = types.KeyboardButton(text='Передать телефон', request_contact=True)
    keyboard.add(bt)
    msg = bot.reply_to(message, "Сообщите телефон для проверки записи", reply_markup=keyboard)
    bot.register_next_step_handler(msg, delete_appoint)


def delete_appoint(message):
    telephone = None
    try:
        telephone = message.contact.phone_number
        tac = message.from_user.username
    except AttributeError:
        msg = bot.reply_to(message, "Надо просто кнопку нажать")
        bot.register_next_step_handler(msg, delete_appoint)
    if telephone != None:
        delete = deleteAppoint(telephone, tac)
        if delete == 'Нет записей':
            text = 'У Вас нет записей'
            msg = bot.send_message(message.chat.id, text)
            user_gritings(message)
        else:
            text = 'Запись успешно удалена'
            msg = bot.send_message(message.chat.id, text)
            user_gritings(message)






@bot.message_handler(commands=['test'])
def make_appoint(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard=True)
    bt = types.KeyboardButton(text='Передать телефон', request_contact=True)
    keyboard.add(bt)
    msg = bot.reply_to(message, "Остался телефон и запись будет готова", reply_markup=keyboard)
    bot.register_next_step_handler(msg, new_test)


def new_test(message):
    bot.send_message(message.chat.id, message.contact.phone_number)

bot.polling()





