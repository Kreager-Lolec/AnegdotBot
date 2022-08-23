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
print("Бот стартує")
CreateTable()
splitword_one = '@;'
splitword_two = '@38)89'


def getCurrentHour():
    utchour = datetime.now()
    if utchour.hour == 21:
        current_hour = 0
    elif utchour.hour == 22:
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


@bot.message_handler(commands=['cmd'])
def start(message):
    if checkIfNoneUserName(message.from_user.username):
        print("No")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            bot.reply_to(message,"Команди для адміністрації: " + "\n" + "/addcategory - Додати категорію для анекдотів" + "\n" + "/addanegdot - Додати анекдот " + "\n" + "/deleteanegdot - Видалити анекдот " + "\n" + "/deletecategory - Видалити категорію")


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
    maxNumOfSymsForCategory = 20
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif len(str(message.text)) <= maxNumOfSymsForCategory:
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
            msg = bot.reply_to(message, f'Назва категорії: "{message.text}" є занадто довгою (максимальна кількість символів: {maxNumOfSymsForCategory} ')
            bot.register_next_step_handler(msg, registerCategory, username)
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
            if checkIfNotExistCategories():
                bot.reply_to(message, "Ви ще не додали категорій, до яких ви будете додавати анекдоти,тому введіть команду /addcategory")
            else:
                markup = InlineKeyboardMarkup()
                markup.width = 3
                for row in getCategories():
                    print(row)
                    print("Size" + str(sys.getsizeof("addaneg: " + message.from_user.username + splitword_one)))
                    print("Size category" + str(sys.getsizeof(row)))
                    markup.add(InlineKeyboardButton(row,
                                                    callback_data="addaneg: " + message.from_user.username + splitword_one + row))
                bot.reply_to(message, "Оберіть категорію, до якої буде відноситися анегдот", reply_markup=markup)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.message_handler(commands=['deleteanegdot'])
def removeanegdot(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            AddChat(message)
            deleteNoneAnegdots()
            if not checkIfNotExistAnedgots():
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                markup.row(item1)
                msg = bot.reply_to(message, "Впишіть анекдот, який хочете видалити", reply_markup=markup)
                bot.register_next_step_handler(msg, removeanegdotfunc, message.from_user.username)
            else:
                bot.reply_to(message, "На жаль, ще не було додано жодного анекдота. Щоб додати - використайте команду /addanegdot")
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


def removeanegdotfunc(message, username):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            if checkIfExistsAnedgotWithoutCategory(str(message.text)):
                removeAnegdotFromDb(str(message.text))
                bot.reply_to(message, "Анекдот успішно видалено!", reply_markup=types.ReplyKeyboardRemove())
            else:
                msg = bot.reply_to(message, "Анекдота не існує, спробуйте надіслати існуючий!")
                bot.register_next_step_handler(msg, removeanegdotfunc, username)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(msg, removeanegdotfunc, username)


@bot.message_handler(commands=['randomanegdot'])
def randomanegdot(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        deleteNoneAnegdots()
        AddChat(message)
        markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton(text="Почитати анекдот по конкретній категорії",
                                     callback_data="chorand: " + message.from_user.username + splitword_one + "readanegdotbycategory")
        item2 = InlineKeyboardButton(text="Почитати анекдот",
                                     callback_data="chorand: " + message.from_user.username + splitword_one + "readanegdot")
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
                                                    callback_data="adelcat: " + message.from_user.username + splitword_one + row))
                bot.reply_to(message, "Список категорій", reply_markup=markup)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("adelcat: "))
def callback_query(call: types.CallbackQuery):
    print(call.from_user.username)
    info = str(call.data).replace("adelcat: ","")
    print("Text: " + call.data)
    info = info.split(splitword_one)
    username = info[0]
    category = info[1]
    if username == call.from_user.username:
        markup = InlineKeyboardMarkup()
        item1 = InlineKeyboardButton(text="Так ✅",
                                     callback_data="delcate: " + call.from_user.username + splitword_one + category)
        item2 = InlineKeyboardButton(text="Ні ⛔",
                                     callback_data="endoper: " + call.from_user.username)
        markup.add(item1, item2)
        bot.reply_to(call.message, 'Ви впевнені, що хочете видалити категорію та анекдоти, які відносяться до неї?.', reply_markup=markup)
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delcate: "))
def callback_query(call: types.CallbackQuery):
    print(call.from_user.username)
    info = str(call.data).replace("delcate: ","")
    info = info.split(splitword_one)
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


@bot.callback_query_handler(func=lambda call: call.data.startswith("endoper: "))
def callback_query(call: types.CallbackQuery):
    print(call.from_user.username)
    username = str(call.data).replace("endoper: ","")
    if username == call.from_user.username:
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(call.message, farewell)
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("addaneg: "))
def callback_query(call: types.CallbackQuery):
    info = str(call.data).replace("addaneg: ","")
    info = info.split(splitword_one)
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


@bot.callback_query_handler(func=lambda call: call.data.startswith("chorand: "))
def callback_query(call: types.CallbackQuery):
    info = str(call.data).replace("chorand: ","")
    info = info.split(splitword_one)
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
                    markup.add(InlineKeyboardButton(row, callback_data="randane: " + call.from_user.username + splitword_one + row))
                bot.reply_to(call.message, "Оберіть категорію анекдота", reply_markup=markup)
        elif answer == "readanegdot":
            if checkIfNotExistAnedgots():
                bot.reply_to(call.message, "Ви ще не додали анекдотів")
            else:
                bot.reply_to(call.message, getAnegdot())
    else:
        bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("randane: "))
def callback_query(call: types.CallbackQuery):
    info = str(call.data).replace("randane: ", "")
    info = info.split(splitword_one)
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


@bot.message_handler(content_types=['text'])
def sendanegdotfromsonya(message):
    if message.text == "@mihailik_panchuk":
        bot.send_audio(chat_id=message.chat.id,audio=open('audio_2022-08-21_14-42-52.MP3', 'rb'))


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


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://whispering-savannah-55697.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

# bot.infinity_polling()
