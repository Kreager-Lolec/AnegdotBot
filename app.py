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


@bot.message_handler(commands=['start'])
def start(message):
    AddChat(message)
    bot.reply_to(message, "Привіт, я буду розказувати вам анегдоти")


@bot.message_handler(commands=['addcategory'])
def addcategory(message):
    if checkIfAdmin(str(message.from_user.username)):
        AddChat(message)
        bot.reply_to(message, "Введіть назву категорії")
        bot.register_next_step_handler(message, registerCategory)
    else:
        bot.reply_to(message, "У вас немає прав на цю дію!")


def registerCategory(message):
    if checkIfExistsCategory(str(message.text)):
        bot.reply_to(message, "Категорія уже існує")
    else:
        addCategory(message)
        bot.reply_to(message, "Категорію успішно додано")
    markup = InlineKeyboardMarkup()
    markup.width = 3
    for row in getCategories():
        markup.add(InlineKeyboardButton(row , callback_data="showanegdot: " + row))
    bot.reply_to(message, "Список категорій", reply_markup=markup)


@bot.message_handler(commands=['addanegdot'])
def addanegdot(message):
    if checkIfAdmin(str(message.from_user.username)):
        AddChat(message)
        markup = InlineKeyboardMarkup()
        markup.width = 3
        for row in getCategories():
            print(row)
            markup.add(InlineKeyboardButton(row, callback_data="addanegdot: " + row))
        bot.reply_to(message, "Оберіть категорію, до якої буде відноситися анегдот", reply_markup=markup)
    else:
        bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.message_handler(commands=['randomanegdot'])
def randomanegdot(message):
    deleteNoneAnegdots()
    AddChat(message)
    markup = InlineKeyboardMarkup()
    item1 = InlineKeyboardButton(text="Почитати анекдот по конкретній категорії",callback_data="chooserand: readanegdotbycategory")
    item2 = InlineKeyboardButton(text="Почитати анекдот",callback_data="chooserand: readanegdot")
    markup.add(item1,item2)
    bot.reply_to(message, 'Оберіть один із варіантів?', reply_markup=markup)


@bot.message_handler(commands=['deletecategory'])
def deletecategory(message):
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
                markup.add(InlineKeyboardButton(row, callback_data="deletecategory: " + row))
            bot.reply_to(message, "Список категорій", reply_markup=markup)
    else:
        bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("deletecategory: "))
def callback_query(call: types.CallbackQuery):
    category = str(call.data).replace("deletecategory: ","")
    if checkIfExistsCategory(category):
        deleteAnegdotsByCategory(category)
        deleteCategory(category)
        bot.reply_to(call.message, "Категорію та анекдоти з неї успішно видалено")
    else:
        bot.reply_to(call.message, "Такої категорії не існує")


@bot.callback_query_handler(func=lambda call: call.data.startswith("addanegdot: "))
def callback_query(call: types.CallbackQuery):
    category = str(call.data).replace("addanegdot: ","")
    msg = bot.reply_to(call.message, "Впишіть ваш анекдот")
    bot.register_next_step_handler(msg, addAnegdot, category)


@bot.callback_query_handler(func=lambda call: call.data.startswith("chooserand: "))
def callback_query(call: types.CallbackQuery):
    answer = str(call.data).replace("chooserand: ","")
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
                markup.add(InlineKeyboardButton(row, callback_data="randomanegdot: " + row))
            bot.reply_to(call.message, "Оберіть категорію анекдота", reply_markup=markup)
    elif answer == "readanegdot":
        if checkIfNotExistAnedgots():
            bot.reply_to(call.message, "Ви ще не додали анекдотів")
        else:
            bot.reply_to(call.message, getAnegdot())


@bot.callback_query_handler(func=lambda call: call.data.startswith("randomanegdot: "))
def callback_query(call: types.CallbackQuery):
    category = str(call.data).replace("randomanegdot: ", "")
    if checkIfNotExistAnedgotsByCategory(category):
        bot.reply_to(call.message, "Ви ще не додали анекдотів для цієї категорії")
    else:
        bot.reply_to(call.message, getAnegdotByCategory(category))



def addAnegdot(message, category):
    if checkIfExistsAnedgot(category, str(message.text)):
        msg = bot.reply_to(message, "Анекдот уже існує, спробуйте надіслати щось нове!")
        bot.register_next_step_handler(msg, addAnegdot, category)
    else:
        addAnegdotToDb(message, category)
        bot.reply_to(message, "Анекдот успішно доданий!")


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
                bot.send_message(row,"Добрий день, сьогодні запропоную вам такий анекдот: " + "\n" + anegdot)


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
