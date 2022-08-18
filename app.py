from dateutil import tz
import Constant_File as Keys
from telebot import *
from telebot.types import *
from ConnectDB import *
from flask import Flask, request
import os



TOKEN = Keys.API_KEY
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


print("Бот стартує")
CreateTable()
splitword = '@3839fji38()#89'


def getCurrentHour():
    utchour = datetime.now()
    if utchour.hour == 21:
        current_hour = 0
    if utchour.hour == 22:
        current_hour = 1
    elif utchour.hour == 23:
        current_hour = 2
    elif utchour.hour == 24:
        current_hour = 3
    else:
        current_hour = utchour.hour + 3
    print(current_hour)
    return current_hour


def getWelcomeAccoringToHours():
    currentHour = getCurrentHour()
    if (currentHour >= 4) and (currentHour < 12):
        return "Доброго ранку"
    elif (currentHour >= 12) and (currentHour < 19):
        return "Добрий день"
    elif (currentHour >= 19) and (currentHour < 24):
        return "Доброго вечора"
    elif (currentHour >= 0) and (currentHour < 4):
        return "Доброї ночі"
    else:
        return "Мої Вітання"


def getFarewellAccoringToHours():
    currentHour = getCurrentHour()
    if (currentHour >= 4) and (currentHour < 12):
        return "Хорошого ранку!"
    elif (currentHour >= 12) and (currentHour < 19):
        return "Хорошого дня!"
    elif (currentHour >= 19) and (currentHour < 24):
        return "Хорошого вечора!"
    elif (currentHour >= 0) and (currentHour < 4):
        return "Хорошої ночі!"
    else:
        return "До зустрічі!"


@bot.message_handler(commands=['start'])
def start(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        AddChat(message)
        bot.reply_to(message, "Привіт, я буду розказувати вам анегдоти")


@bot.message_handler(commands=['addcategory'])
def addcategory(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            AddChat(message)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            bot.reply_to(message, "Введіть назву категорії", reply_markup=markup)
            bot.register_next_step_handler(message, registerCategory, message.from_user.username)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


def registerCategory(message, username):
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            if checkIfExistsCategory(str(message.text)):
                msg = bot.reply_to(message, "Категорія уже існує, спробуйте надіслати щось нове!")
                bot.register_next_step_handler(msg, registerCategory, username)
            else:
                addCategory(message)
                bot.reply_to(message, "Категорію успішно додано", reply_markup=types.ReplyKeyboardRemove())
            markup = InlineKeyboardMarkup()
            markup.width = 3
            for row in getCategories():
                markup.add(InlineKeyboardButton(row, callback_data="showanegdot: " + row))
            bot.reply_to(message, "Список категорій", reply_markup=markup)
    else:
        bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(message, registerCategory, username)


@bot.message_handler(commands=['addanegdot'])
def addanegdot(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            AddChat(message)
            markup = InlineKeyboardMarkup()
            markup.width = 3
            for row in getCategories():
                print(row)
                markup.add(InlineKeyboardButton(row,
                                                callback_data="addanegdot: " + message.from_user.username + splitword + row))
            bot.reply_to(message, "Оберіть категорію, до якої буде відноситися анегдот", reply_markup=markup)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.message_handler(commands=['randomanegdot'])
def randomanegdot(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        deleteNoneAnegdots()
        AddChat(message)
        markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton(text="Почитати анекдот по конкретній категорії",
                                     callback_data="chooserand: " + message.from_user.username + splitword + "readanegdotbycategory")
        item2 = InlineKeyboardButton(text="Почитати анекдот",
                                     callback_data="chooserand: " + message.from_user.username + splitword + "readanegdot")
        markup.add(item1, item2)
        bot.reply_to(message, 'Оберіть один із варіантів.', reply_markup=markup)


@bot.message_handler(commands=['deletecategory'])
def deletecategory(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            AddChat(message)
            markup = InlineKeyboardMarkup()
            markup.width = 3
            listOfCategories = getCategories()
            if not listOfCategories:
                bot.reply_to(message, "Ви ще не додали категорій")
            else:
                for row in listOfCategories:
                    print(row)
                    markup.add(InlineKeyboardButton(row,
                                                    callback_data="acceptdeletecategory: " + message.from_user.username + splitword + row))
                bot.reply_to(message, "Список категорій", reply_markup=markup)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("acceptdeletecategory: "))
def callback_query(call: types.CallbackQuery):
    print(call.from_user.username)
    info = str(call.data).replace("acceptdeletecategory: ","")
    info = info.split(splitword)
    username = info[0]
    category = info[1]
    if username == call.from_user.username:
        markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton(text="Так ✅",
                                     callback_data="deletecategory: " + call.from_user.username + splitword + category)
        item2 = InlineKeyboardButton(text="Ні ⛔",
                                     callback_data="endoperation: " + call.from_user.username)
        markup.add(item1, item2)
        bot.reply_to(call.message, 'Ви впевнені, що хочете видалити категорію та анекдоти, які відносяться до неї?.', reply_markup=markup)
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("deletecategory: "))
def callback_query(call: types.CallbackQuery):
    print(call.from_user.username)
    info = str(call.data).replace("deletecategory: ","")
    info = info.split(splitword)
    username = info[0]
    category = info[1]
    if username == call.from_user.username:
        if checkIfExistsCategory(category):
            deleteAnegdotsByCategory(category)
            deleteCategory(category)
            bot.reply_to(call.message, "Категорію та анекдоти з неї успішно видалено")
        else:
            bot.reply_to(call.message, "Такої категорії не існує")
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("endoperation: "))
def callback_query(call: types.CallbackQuery):
    print(call.from_user.username)
    username = str(call.data).replace("endoperation: ","")
    if username == call.from_user.username:
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(call.message, farewell)
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("addanegdot: "))
def callback_query(call: types.CallbackQuery):
    info = str(call.data).replace("addanegdot: ","")
    info = info.split(splitword)
    username = info[0]
    category = info[1]
    if username == call.from_user.username:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("🛑 Відмінити операцію!")
        markup.row(item1)
        msg = bot.reply_to(call.message, "Впишіть ваш анекдот", reply_markup=markup)
        bot.register_next_step_handler(msg, addAnegdot, category, username)
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("chooserand: "))
def callback_query(call: types.CallbackQuery):
    info = str(call.data).replace("chooserand: ","")
    info = info.split(splitword)
    username = info[0]
    answer = info[1]
    print(info)
    print(call.from_user.username)
    if username == call.from_user.username:
        if answer == "readanegdotbycategory":
            listOfCategories = getCategories()
            if not listOfCategories:
                bot.reply_to(call.message, "Ви ще не додали категорій")
            elif checkIfNotExistAnedgots():
                bot.reply_to(call.message, "Ви ще не додали анекдотів")
            else:
                markup = InlineKeyboardMarkup()
                markup.width = 3
                for row in listOfCategories:
                    print(row)
                    markup.add(InlineKeyboardButton(row, callback_data="randomanegdot: " + call.from_user.username + splitword + row))
                bot.reply_to(call.message, "Оберіть категорію анекдота", reply_markup=markup)
        elif answer == "readanegdot":
            if checkIfNotExistAnedgots():
                bot.reply_to(call.message, "Ви ще не додали анекдотів")
            else:
                bot.reply_to(call.message, getAnegdot())
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("randomanegdot: "))
def callback_query(call: types.CallbackQuery):
    info = str(call.data).replace("randomanegdot: ", "")
    info = info.split(splitword)
    username = info[0]
    category = info[1]
    if username == call.from_user.username:
        if checkIfNotExistAnedgotsByCategory(category):
            bot.reply_to(call.message, "Ви ще не додали анекдотів для цієї категорії")
        else:
            bot.reply_to(call.message, getAnegdotByCategory(category))
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")



def addAnegdot(message, category, username):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            if checkIfExistsAnedgot(category, str(message.text)):
                msg = bot.reply_to(message, "Анекдот уже існує, спробуйте надіслати щось нове!")
                bot.register_next_step_handler(msg, addAnegdot, category, username)
            else:
                addAnegdotToDb(message, category)
                bot.reply_to(message, "Анекдот успішно доданий!", reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(msg, addAnegdot, category, username)


def checkIfNoneUserName(username):
    if username == 'None':
        return True
    return False


def my_interval_job():
    if checkIfExistChats():
        deleteNoneAnegdots()
        listId = GetChatsId()
        print(listId)
        for row in listId:
            if checkIfNotExistAnedgots():
                bot.send_message(row, 'Анекдотів поки що немає.')
            else:
                anegdot = str(getAnegdot())
                welcome = getWelcomeAccoringToHours()
                print(welcome)
                try:
                    bot.send_message(row, welcome + ", сьогодні запропоную вам такий анекдот: " + "\n" + anegdot)
                except:
                    DeleteChat(row)
                    my_interval_job()



@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://still-peak-85834.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

# bot.infinity_polling()
