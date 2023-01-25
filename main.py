import json
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, Filters, MessageHandler, BaseFilter, TypeHandler
from commands import nearestEntry
from jsonfilepy import jsonread, jsonwright
jsondict = jsonread()





while (True):
    print('Что нужно сделать')
    print('1 - Ближайшая запись')
    print('2 - Проверить запись на конкретную дату')
    print('3 - Режим работы')
    print('4 - Осуществить запись')
    print('5 - Отменить запись')
    command = input('Введи команду\n')
    if command == '1':
        nearestEntry(jsondict)
    if command == '0':
        break