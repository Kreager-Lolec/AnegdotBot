from dateutil import tz
import Constant_File as Keys
from telebot import *
from telebot.types import *
from ConnectDB import *
from apscheduler.schedulers.background import BackgroundScheduler


TOKEN = Keys.API_KEY
bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
# deleteExactlyAnegdots()
# deleteExactlyCategories()
# deleteExactlyAdmin()
# server = Flask(__name__)


def send_something():
    ShowChats()


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


scheduler.add_job(send_something, 'interval', minutes=29, seconds=59)
scheduler.add_job(my_interval_job, 'cron', hour='8,20')
scheduler.start()

print("Бот стартує")
# DropTable()
CreateTable()
splitword_one = '@;'
splitword_two = '@38)89'
roleName = ['Юнлінг', 'Падаван', 'Лицар-джедай', 'гранд-майстер Ордена джедаїв']
listRights = ['addcategory', 'addanegdot', 'deletecategory', 'deleteanegdot', 'gettxtanegdot', 'gettxtadmins', 'controladmin', 'inserttxtcategoriesandanegdotstodb', 'inserttxtadminstodb']
listUnlingRights = listRights[0] + ";" + listRights[1]
listPadavanRights = listUnlingRights + ";" + listRights[2] + ";" + listRights[3]
listJediKnightRights = listPadavanRights + ";" + listRights[4] + ";" + listRights[5]
listGrandMasterRights = listJediKnightRights + ";" + listRights[6] + ";" + listRights[7] + ";" + listRights[8]
maxNumOfSymsForAnegdot = 510
maxNumOfSymsForAdmins = 54


# bot.send_message(612268517, "Саня отшила як обично, все понятно")


def getCurrentHour():
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.utcnow()
    utc = utc.replace(tzinfo=from_zone)
    current_hour = utc.astimezone(to_zone)
    print(current_hour.hour)
    # now = datetime.utcnow()
    # if now.hour == 22:
    #     current_hour = 1
    # elif now.hour == 23:
    #     current_hour = 2
    # elif now.hour == 24:
    #     current_hour = 3
    # else:
    #     current_hour = now.hour + 3
    return current_hour.hour


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
    print("Id:" + str(message.from_user.id))
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        AddChat(message)
        print(message.from_user.id)
        bot.reply_to(message, "Привіт, я буду розказувати вам анегдоти")


@bot.message_handler(commands=['cmd'])
def cmd(message):
    if checkIfNoneUserName(message.from_user.username):
        print("No")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            info = ""
            adminRights = str(GetAdminRights(message.from_user.username))
            print("AdminRights: " + adminRights)
            if listUnlingRights in adminRights:
                info += "Команди для адміністрації: " + "\n" + "/addcategory - Додати категорію для анекдотів" + "\n" + "/addanegdot - Додати анекдот" + "\n"
            if listPadavanRights in adminRights:
                info += "/deleteanegdot - Видалити анекдот" + "\n" + "/deletecategory - Видалити категорію" + "\n"
            if listJediKnightRights in adminRights:
                info += "/gettxtanegdot - Витягнути анекдоти з бази даних" + "\n" + "/gettxtadmins - Витягнути адмінів з бази даних" + "\n"
            if listGrandMasterRights in adminRights:
                info += "/controladmin - Контролюєм адмінів!" + "\n" + "/inserttxtcategoriesandanegdotstodb - Затягнути категорії та анекдоти в базу даних" + "\n" + "/inserttxtadminstodb - Затягнути адмінів в базу даних"
            bot.reply_to(message,info)


@bot.message_handler(commands=['controladmin'])
def controladmin(message):
    if checkIfNoneUserName(message.from_user.username):
        print("No")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            adminRights = str(GetAdminRights(message.from_user.username))
            print("AdminRights: " + adminRights)
            if listGrandMasterRights in adminRights:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, )
                item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                markup.row(item1)
                msg = bot.reply_to(message, "Введіть username кандидата, для того щоб увійти в панель управління адміністрацією.", reply_markup=markup)
                bot.register_next_step_handler(msg, controlAdminPanel, message.from_user.username)


@bot.message_handler(commands=['proposeajokeandcategory'])
def proposeajokecategory(message):
    print("Id:" + str(message.from_user.id))
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        AddChat(message)
        print(str(message.from_user.id))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        item1 = types.KeyboardButton("Додати")
        item2 = types.KeyboardButton("Видалити")
        item3 = types.KeyboardButton("🛑 Відмінити операцію!")
        markup.row(item1, item2)
        markup.row(item3)
        msg = bot.reply_to(message, "Привіт, ви хочете запропонувати додати анекдот/категорію чи видалити?", reply_markup=markup)
        bot.register_next_step_handler(msg, proccesajoke, message.from_user.username, message.from_user.id)


def controlAdminPanel(message, username):
    stringbyte = "addadmin: " + message.text
    print("Bytes Message.text: " + str(len(message.text.encode('utf-8'))))
    print("Bytes stringbyte: " + str(len(stringbyte.encode('utf-8'))))
    if len(message.text.encode('utf-8')) <= maxNumOfSymsForAdmins:
        if username == message.from_user.username:
            if message.text == "🛑 Відмінити операцію!":
                farewell = getFarewellAccoringToHours()
                print(farewell)
                bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
            elif message.text is None:
                msg = bot.reply_to(message, f'Я був би не проти нюдсів блонд, але пришліть будь ласка мені username')
                bot.register_next_step_handler(msg, controlAdminPanel, username)
            elif str(message.text).count("||") > 0 or str(message.text).count("//") > 0:
                msg = bot.reply_to(message, f'На жаль username не може містити набір символів "||" або "//", спробуйте ще раз')
                bot.register_next_step_handler(msg, controlAdminPanel, username)
            else:
                newAdminUsername = str(message.text)
                markup = InlineKeyboardMarkup()
                markup.width = 3
                markup.add(InlineKeyboardButton(f'Додати {message.text} до адміністраторів?',
                                                callback_data="addadmin: " + newAdminUsername))
                markup.add(InlineKeyboardButton(f'Забрати {message.text} адміністраторські права?',
                                                callback_data="remoadm: " + newAdminUsername))
                msg = bot.reply_to(message, "ㅤ", reply_markup=types.ReplyKeyboardRemove())
                bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                bot.reply_to(message, "Оберіть один з варіантів", reply_markup=markup)
        else:
            msg = bot.reply_to(message, f'Зараз черга {username}')
            bot.register_next_step_handler(msg, controlAdminPanel, username)
    else:
        msg = bot.reply_to(message,
                           "Ви перевищили ліміт символів ( 54 - для латиниці, 27 - для кирилиці ), спробуйте ще раз!")
        bot.register_next_step_handler(msg, controlAdminPanel, username)


@bot.callback_query_handler(func=lambda call: call.data.startswith("addadmin: "))
def callback_query(call: types.CallbackQuery):
    if checkIfAdmin(str(call.from_user.username)):
        newAdminUserName = str(call.data).replace("addadmin: ", "")
        if newAdminUserName == "kreager" and call.from_user.username == "kreager":
            msg = bot.reply_to(call.message, "Гранд-Майстре, якщо ви хочете себе вбити, то скажіть @alexagranv ще раз, що вона вам подобається.")
            bot.register_next_step_handler(msg, controlAdminPanel, call.from_user.username)
        elif newAdminUserName == "kreager":
            msg = bot.reply_to(call.message, "У вас недостатньо сили, щоб зкинути Гранд-Майстра")
            bot.register_next_step_handler(msg, controlAdminPanel, call.from_user.username)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Так ✅")
            item2 = types.KeyboardButton("Ні ⛔")
            markup.row(item1, item2)
            msg = bot.reply_to(call.message,
                               'Ви впевнені?',
                               reply_markup=markup)
            bot.register_next_step_handler(msg, addAdmin, newAdminUserName, call.from_user.username)
    else:
        print(f'{call.from_user.username} is not an admin')


@bot.callback_query_handler(func=lambda call: call.data.startswith("remoadm: "))
def callback_query(call: types.CallbackQuery):
    if checkIfAdmin(str(call.from_user.username)):
        deleteAdminUserName = str(call.data).replace("remoadm: ", "")
        if deleteAdminUserName == "kreager" and call.from_user.username == "kreager":
            msg = bot.reply_to(call.message,"Гранд-Майстре, якщо ви хочете себе вбити, то скажіть @alexagranv ще раз, що вона вам подобається.")
            bot.register_next_step_handler(msg, controlAdminPanel, call.from_user.username)
        elif deleteAdminUserName == "kreager":
            msg = bot.reply_to(call.message,"У вас недостатньо сили, щоб зкинути Гранд-Майстра")
            bot.register_next_step_handler(msg, controlAdminPanel, call.from_user.username)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Так ✅")
            item2 = types.KeyboardButton("Ні ⛔")
            markup.row(item1, item2)
            msg = bot.reply_to(call.message,
                               'Ви впевнені?',
                               reply_markup=markup)
            bot.register_next_step_handler(msg, removeAdmin, deleteAdminUserName, call.from_user.username)
    else:
        print(f'{call.from_user.username} is not an admin')


def removeAdmin(message, deleteAdminUserName, username):
    if username == message.from_user.username:
        if message.text == "Так ✅":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton(roleName[0])
            item2 = types.KeyboardButton(roleName[1])
            item3 = types.KeyboardButton(roleName[2])
            item4 = types.KeyboardButton(roleName[3])
            item5 = types.KeyboardButton("Забрати усі права.")
            markup.row(item1, item2)
            markup.row(item3, item4, item5)
            msg = bot.reply_to(message, "Оберіть роль, з якої ви хочете зняти людини", reply_markup=markup)
            bot.register_next_step_handler(msg, removerole, deleteAdminUserName, username)
        elif message.text == "Ні ⛔":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message,f'Зараз черга {username}')
        bot.register_next_step_handler(msg, removeAdmin, deleteAdminUserName, username)


def removerole(message, deleteAdminUserName, userName):
    if message.from_user.username == userName:
        role = str(message.text)
        deleteAdminUserNameProcces = str(deleteAdminUserName).strip(" ")
        deleteAdminUserNameProcces = str(deleteAdminUserNameProcces).replace("@","")
        if role == "Забрати усі права." and checkIfAdmin(deleteAdminUserNameProcces):
            deleteAdmin(deleteAdminUserNameProcces)
            removeAdminRoleWhileSetNew(deleteAdminUserNameProcces)
            bot.reply_to(message,
                         f'У адміна {deleteAdminUserName} успішно забрано права за порушення ПСР (Правил Смішного Руху)',
                         reply_markup=types.ReplyKeyboardRemove())
        elif role == "Забрати усі права.":
            msg = bot.reply_to(message, f"Адміна {deleteAdminUserName} не існує.", reply_markup=types.ReplyKeyboardRemove())
        elif checkIfAdminHaveRole(deleteAdminUserNameProcces, role):
                deleteAdmin(deleteAdminUserNameProcces)
                removeAdminRole(deleteAdminUserNameProcces, role)
                bot.reply_to(message, f'Адміна {deleteAdminUserName} успішно знято з ролі {role}',
                             reply_markup=types.ReplyKeyboardRemove())
                getAdminListByRole(role)
        else:
            msg = bot.reply_to(message, f"Адміна {deleteAdminUserName} з такою роллю {role} не існує, спробуйте вибрати іншу роль.")
            bot.register_next_step_handler(msg, removeAdmin, deleteAdminUserName, userName)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{userName}.")
        bot.register_next_step_handler(msg, removeAdmin, deleteAdminUserName, userName)


def addAdmin(message, newAdminUserName, username):
    if username == message.from_user.username:
        if message.text == "Так ✅":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton(roleName[0])
            item2 = types.KeyboardButton(roleName[1])
            item3 = types.KeyboardButton(roleName[2])
            item4 = types.KeyboardButton(roleName[3])
            markup.row(item1, item2)
            markup.row(item3, item4)
            msg = bot.reply_to(message, "Оберіть роль, на яку піде людина", reply_markup=markup)
            bot.register_next_step_handler(msg, addrole, newAdminUserName, username)
        elif message.text == "Ні ⛔":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
    else:
        msg = bot.reply_to(message,f'Зараз черга {username}')
        bot.register_next_step_handler(msg, addAdmin, newAdminUserName, username)


def addrole(message, newAdminUserName, userName):
    if message.from_user.username == userName:
        role = str(message.text)
        newAdminUserNameProcces = str(newAdminUserName).strip(" ")
        newAdminUserNameProcces = str(newAdminUserNameProcces).replace("@","")
        if checkIfAdminHaveRole(newAdminUserNameProcces,role):
            msg = bot.reply_to(message, f"Адмін @{newAdminUserNameProcces} уже має роль {role}.",reply_markup=types.ReplyKeyboardRemove())
        else:
            removeAdminRoleWhileSetNew(newAdminUserNameProcces)
            deleteAdmin(newAdminUserNameProcces)
            addAdminToDb(newAdminUserNameProcces, userName)
            addAdminRole(newAdminUserNameProcces, role)
            bot.reply_to(message, f'Адмін {newAdminUserName} успішно доданий на роль {role}',
                         reply_markup=types.ReplyKeyboardRemove())
            getAdminListByRole(role)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{userName}.")
        bot.register_next_step_handler(msg, addAdmin, newAdminUserName, userName)


def proccesajoke(message, username, userid):
    if username == message.from_user.username:
        if message.text == "Додати":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Запропонувати лише анекдот")
            item2 = types.KeyboardButton("Запропонувати лише категорію")
            item3 = types.KeyboardButton("Запропонувати обидві")
            item4 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1, item2)
            markup.row(item3, item4)
            msg = bot.reply_to(message, "Запропонуйте ваш анекдот.", reply_markup=markup)
            bot.register_next_step_handler(msg, proccesaddjoke, username, userid)
        elif message.text == "Видалити":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Запропонувати лише анекдот")
            item2 = types.KeyboardButton("Запропонувати лише категорію")
            item3 = types.KeyboardButton("Запропонувати обидві")
            item4 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1, item2)
            markup.row(item3, item4)
            msg = bot.reply_to(message, "Запропонуйте анекдот для видалення.", reply_markup=markup)
            bot.register_next_step_handler(msg, proccesdeletejoke, username, userid)
        elif message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            msg = bot.reply_to(message,
                               "Ви перевищили ліміт символів ( максимальна кількість - 510 ), спробуйте ще раз!")
            bot.register_next_step_handler(msg, proccesajoke, username, userid)
    else:
        msg = bot.reply_to(message,f'Зараз черга {username}')
        bot.register_next_step_handler(msg, proccesajoke, username, userid)


def proccesaddjoke(message, username, userid):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "Запропонувати лише анекдот":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            msg = bot.reply_to(message, "Введіть назву анекдота", reply_markup=markup)
            bot.register_next_step_handler(msg, proccesregisterAnegdot, username)
        elif message.text == "Запропонувати лише категорію":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            msg = bot.reply_to(message, "Введіть назву категорії", reply_markup=markup)
            bot.register_next_step_handler(msg, proccesregisterCategory, username)
        elif message.text == "Запропонувати обидві":
            if len(str(message.text)) <= maxNumOfSymsForAnegdot:
                if checkIfExistsAnedgotWithoutCategory(str(message.text)):
                    msg = bot.reply_to(message, "Анекдот уже існує, спробуйте надіслати щось нове!")
                    bot.register_next_step_handler(msg, proccesaddjoke, username, userid)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                    markup.row(item1)
                    msg = bot.reply_to(message, "Введіть категорію, до якої хочете додати анекдот?",
                                   reply_markup=markup)
                    bot.register_next_step_handler(msg, proccesaddjokecategory, str(message.text), username, userid)
        else:
            bot.register_next_step_handler(message, proccesaddjoke, username, userid)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(msg, proccesaddjoke, username, userid)


def proccesregisterAnegdot(message, username):
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
            if len(str(message.text)) <= maxNumOfSymsForAnegdot:
                if checkIfExistsAnedgotWithoutCategory(str(message.text)):
                    msg = bot.reply_to(message, "Анекдот уже існує, спробуйте надіслати щось нове!")
                    bot.register_next_step_handler(msg, proccesregisterAnegdot, username)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                    item2 = types.KeyboardButton("Так ✅")
                    item3 = types.KeyboardButton("Ні ⛔")
                    markup.row(item2, item3)
                    markup.row(item1)
                    msg = bot.reply_to(message, "Ви підтверджуєте свої дії?",
                                       reply_markup=markup)
                    bot.register_next_step_handler(msg, proccesaddjokecategory, str(message.text), username)
            else:
                msg = bot.reply_to(message,
                                   "Ви перевищили ліміт символів ( максимальна кількість - 510 ), спробуйте ще раз!")
                bot.register_next_step_handler(msg, proccesregisterAnegdot, username)
    else:
        bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(message, proccesregisterAnegdot, username)


def proccesregisterCategory(message, username):
    maxNumOfSymsForCategory = 55
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif len(message.text.encode('utf-8')) <= maxNumOfSymsForCategory:
            if checkIfExistsCategory(str(message.text)):
                msg = bot.reply_to(message, "Категорія уже існує, спробуйте надіслати щось нове!")
                bot.register_next_step_handler(msg, proccesregisterCategory, username)
            else:
                addCategory(message)
                bot.reply_to(message, "Категорію успішно додано", reply_markup=types.ReplyKeyboardRemove())
            markup = InlineKeyboardMarkup()
            markup.width = 3
            for row in getCategories():
                markup.add(InlineKeyboardButton(row, callback_data="showane: " + row))
            bot.reply_to(message, "Список категорій", reply_markup=markup)
        else:
            msg = bot.reply_to(message, f'Назва категорії: "{message.text}" є занадто довгою ( максимальна кількість символів: ( 55 - для латиниці, 27 - для кирилиці) )')
            bot.register_next_step_handler(msg, proccesregisterCategory, username)
    else:
        bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(message, proccesregisterCategory, username)


def proccesaddjokecategory(message, joke, username, userid):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "Так ✅":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            msg = bot.reply_to(message, "Введіть назву категорії", reply_markup=markup)
            bot.register_next_step_handler(msg, sendadminjoke, joke, username, userid)
        elif message.text == "Ні ⛔":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            markup = InlineKeyboardMarkup()
            markup.width = 3
            for row in getCategories():
                print(sys.getsizeof(row))
                markup.add(InlineKeyboardButton(row, callback_data="showane: " + row))
            bot.reply_to(message, "Оберіть категорію, до якої хочете додати свій анекдот", reply_markup=markup)
            bot.reply_to(message, "Ваший анекдот відправлений на обробку адміністратором.", reply_markup=types.ReplyKeyboardRemove())
            sendadminjoke(message, joke, username, userid)
        else:
            bot.register_next_step_handler(message, proccesaddjokecategory, joke, username, userid)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(msg, proccesaddjokecategory, joke, username, userid)


def proccesdeletejoke(message, username, userid):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "Запропонувати лише анекдот":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            msg = bot.reply_to(message, "Введіть назву анекдота", reply_markup=markup)
            bot.register_next_step_handler(msg, proccesdeleteAnegdot, username)
        elif message.text == "Запропонувати лише категорію":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            msg = bot.reply_to(message, "Введіть назву категорії", reply_markup=markup)
            bot.register_next_step_handler(msg, proccesdeleteCategory, username)
        elif message.text == "Запропонувати обидві":
            if len(str(message.text)) <= maxNumOfSymsForAnegdot:
                if checkIfExistsAnedgotWithoutCategory(str(message.text)):
                    msg = bot.reply_to(message, "Анекдот уже існує, спробуйте надіслати щось нове!")
                    bot.register_next_step_handler(msg, proccesdeletejoke, username, userid)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                    markup.row(item1)
                    msg = bot.reply_to(message, "Введіть категорію, до якої хочете додати анекдот?",
                                       reply_markup=markup)
                    bot.register_next_step_handler(msg, proccesdeletejokecategory, str(message.text), username, userid)
        else:
            bot.register_next_step_handler(message, proccesdeletejoke, username, userid)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(msg, proccesdeletejoke, username, userid)


def proccesdeleteAnegdot(message, username):
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
            if len(str(message.text)) <= maxNumOfSymsForAnegdot:
                if checkIfExistsAnedgotWithoutCategory(str(message.text)):
                    msg = bot.reply_to(message, "Анекдот уже існує, спробуйте надіслати щось нове!")
                    bot.register_next_step_handler(msg, proccesregisterAnegdot, username)
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                    markup.row(item1)
                    msg = bot.reply_to(message, ".",
                                       reply_markup=markup)
                    bot.register_next_step_handler(msg, proccesaddjokecategory, str(message.text), username)
            else:
                msg = bot.reply_to(message,
                                   "Ви перевищили ліміт символів ( максимальна кількість - 510 ), спробуйте ще раз!")
                bot.register_next_step_handler(msg, proccesregisterAnegdot, username)
    else:
        bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(message, proccesregisterAnegdot, username)


def proccesdeleteCategory(message, username):
    maxNumOfSymsForCategory = 55
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif len(message.text.encode('utf-8')) <= maxNumOfSymsForCategory:
            if checkIfExistsCategory(str(message.text)):
                msg = bot.reply_to(message, "Категорія уже існує, спробуйте надіслати щось нове!")
                bot.register_next_step_handler(msg, proccesregisterCategory, username)
            else:
                addCategory(message)
                bot.reply_to(message, "Категорію успішно додано", reply_markup=types.ReplyKeyboardRemove())
            markup = InlineKeyboardMarkup()
            markup.width = 3
            for row in getCategories():
                print(sys.getsizeof(row))
                markup.add(InlineKeyboardButton(row, callback_data="showane: " + row))
            bot.reply_to(message, "Список категорій", reply_markup=markup)
        else:
            msg = bot.reply_to(message, f'Назва категорії: "{message.text}" є занадто довгою ( максимальна кількість символів: ( 55 - для латиниці, 27 - для кирилиці) )')
            bot.register_next_step_handler(msg, proccesregisterCategory, username)
    else:
        bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(message, proccesregisterCategory, username)


def proccesdeletejokecategory(message, joke, username, userid):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif message.text == "Так ✅":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            msg = bot.reply_to(message, "Введіть назву категорії", reply_markup=markup)
            bot.register_next_step_handler(msg, sendadminjoke, joke, username, userid)
        elif message.text == "Ні ⛔":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            markup = InlineKeyboardMarkup()
            markup.width = 3
            for row in getCategories():
                print(sys.getsizeof(row))
                markup.add(InlineKeyboardButton(row, callback_data="showane: " + row))
            bot.reply_to(message, "Оберіть категорію, до якої хочете додати свій анекдот", reply_markup=markup)
            bot.reply_to(message, "Ваший анекдот відправлений на обробку адміністратором.", reply_markup = types.ReplyKeyboardRemove())
            sendadminjoke(message, joke, username, userid)
        else:
            bot.register_next_step_handler(message, proccesaddjokecategory, joke, username, userid)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(msg, proccesaddjokecategory, joke, username, userid)


def sendadminjoke(message, joke, username, userid):
    bot.reply_to(message, "Ваший анекдот відправлений на обробку адміністратором.",
                 reply_markup=types.ReplyKeyboardRemove())
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Так ✅")
    item2 = types.KeyboardButton("Ні ⛔")
    item3 = types.KeyboardButton("🛑 Відмінити операцію!")
    markup.row(item1, item2)
    markup.row(item3)
    # bot.send_message(156911032, "@" + username + " запропонував такий анекдот: " + joke + " у таку категорію: " + message.text, reply_markup=markup)
    msg = bot.send_message(256266717, "@" + username + " запропонував такий анекдот: " + joke + " у таку категорію: " + message.text, reply_markup=markup)
    bot.register_next_step_handler(msg, approveornojoke, username, userid, joke, message.text)


def approveornojoke(message, username, userid, joke, categoryjoke):
    if message.text == "🛑 Відмінити операцію!":
        farewell = getFarewellAccoringToHours()
        print(farewell)
        bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Так ✅":
        if checkIfExistsCategory(proccesAnegdotOrCategoryName(categoryjoke)):
            addAnegdotToDbApprove(joke, categoryjoke, username)
        else:
            addCategoryApprove(categoryjoke, username)
            addAnegdotToDbApprove(joke, categoryjoke, username)
        msg = bot.send_message(userid, "Запропонований вами анекдот: " + joke + " успішно прийнято та додано.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, sendadminjoke, joke, username, userid)
    elif message.text == "Ні ⛔":
        msg = bot.send_message(userid, "Запропонований вами анекдот: " + joke + " відхилено, випробуйте вашу вдачу ще раз /proposeajoke.", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, sendadminjoke, joke, username, userid)





@bot.message_handler(commands=['gettxtanegdot'])
def gettxtanegdot(message):
    private_chat_id = message.from_user.id
    if checkIfAdmin(str(message.from_user.username)):
        adminRights = str(GetAdminRights(message.from_user.username))
        if listJediKnightRights in adminRights:
            if checkIfNotExistCategories():
                bot.send_message(private_chat_id, "На жаль, у базі даних ще немає категорій")
            else:
                if checkIfNotExistAnedgots():
                    bot.send_message(private_chat_id, "На жаль, у базі даних ще немає анекдотів")
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("Для перегляду")
                    item2 = types.KeyboardButton("Для бази даних")
                    item3 = types.KeyboardButton("🛑 Відмінити операцію!")
                    markup.row(item1, item2)
                    markup.row(item3)
                    msg = bot.send_message(private_chat_id, "Для чого вам потрібен файл", reply_markup=markup)
                    bot.register_next_step_handler(msg, gettxtfileanegdot,message.from_user.username)


def gettxtfileanegdot(message, username):
    if message.from_user.username == username:
        with open('listAnegdots.txt', 'w', encoding='utf-8') as f:
            info = ""
            if message.text == "Для перегляду":
                for row in getFullInfoCategories():
                    info += "Category: " + row[1]
                    info += " | "
                    info += "Who added: " + row[3]
                    # info += " Time, when added: " + row[4]
                    info += "\n"
                    info += "List of anegdots: \n"
                    if checkIfNotExistAnedgotsByCategory(row[1]):
                        info += "Анекдотів у цій категорії ще немає"
                        info += "\n"
                    else:
                        for row in getFullInfoAnegdotsByCategory(row[1]):
                            info += "Anegdot: " + row[1]
                            info += " | "
                            info += "Who added: " + row[5]
                            # info += " Time, when added: " + row[6]
                            info += "\n"
                    info += "\n\n"
            elif message.text == "Для бази даних":
                for row in getFullInfoCategories():
                    datedata = str(row[4]).replace("\n", "")
                    info += "Category: " + row[1] + "||" + row[3] + "||" + datedata + "||||\n"
                    print(str(row[4]))
                    # info += " Time, when added: " + row[4]
                    # info += "\n"
                    for row in getFullInfoAnegdotsByCategory(row[1]):
                        datedata = str(row[6]).replace("\n", "")
                        info += "Anegdot: " + row[1] + "||" + row[3] + "||" + row[5] + "||" + datedata + "||||\n"
                        print(str(row[6]))
                        # info += "\n"
            elif message.text == "🛑 Відмінити операцію!":
                farewell = getFarewellAccoringToHours()
                print(farewell)
                bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.register_next_step_handler(message, gettxtfileanegdot, username)
            print(info)
            f.write(info)
        bot.send_document(message.from_user.id, open(r'listAnegdots.txt', 'rb'), reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['inserttxtcategoriesandanegdotstodb'])
def inserttxtanegdottodb(message):
    if checkIfAdmin(str(message.from_user.username)):
        adminRights = str(GetAdminRights(message.from_user.username))
        if listGrandMasterRights in adminRights:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            private_chat_id = message.from_user.id
            msg = bot.send_message(private_chat_id, "Пришліть текстовий файл з анекдотами", reply_markup=markup)
            bot.register_next_step_handler(msg, handle_document_anegdot, message.from_user.username)


def handle_document_anegdot(message,username):
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            try:
                file_name = message.document.file_name
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                with open("listAnegdotsProcces.txt", 'wb') as new_file:
                    # print(downloaded_file)
                    new_file.write(downloaded_file)
                proccesDocumentAnegdot(message, username)
            except:
                msg = bot.reply_to(message, "Пришліть будь ласка текстовий файл!")
                bot.register_next_step_handler(msg, handle_document_anegdot, username)




@bot.message_handler(commands=['inserttxtadminstodb'])
def inserttxtadminstodb(message):
    if checkIfAdmin(str(message.from_user.username)):
        adminRights = str(GetAdminRights(message.from_user.username))
        if listGrandMasterRights in adminRights:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            private_chat_id = message.from_user.id
            msg = bot.send_message(private_chat_id, "Пришліть текстовий файл зі списком адмінів", reply_markup=markup)
            bot.register_next_step_handler(msg, handle_document_admin, message.from_user.username)


def handle_document_admin(message, username):
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            # try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                with open("listAdminsProcces.txt", 'wb') as new_file:
                    # print(downloaded_file)
                    new_file.write(downloaded_file)
                proccesDocumentAdmin(message, username)
            # except:
            #     msg = bot.reply_to(message, "Пришліть будь ласка текстовий файл!")
            #     bot.register_next_step_handler(msg, handle_document_admin, username)


def proccesDocumentAdmin(message, username):
    with open("listAdminsProcces.txt", 'r', encoding="utf8") as fileAdmin:
        lines = fileAdmin.readlines()
        listAdmins = ""
        listUnling = ""
        listPadavan = ""
        listKnigtJedi = ""
        listGrandMaster = ""
        listadminsAdding = False
        listUnlingAdding = False
        listPadavanAdding = False
        listKnigtJediAdding = False
        listGrandMasterAdding = False
        # try:
        countAdded = 0
        countReAdded = 0
        for row in lines:
                print("New Unling loop ================= " + "Number of added: " + str(
                    countAdded) + "; Number of readded: " + str(
                    countReAdded) + "; Number |||| " + str(listUnling.count("||||")))
                if "Юнлінг" in row:
                    listUnling = row.replace("\n", "")
                    print("New Unling row: " + listUnling)
                    listUnlingAdding = True
                if listUnlingAdding:
                    if listUnling.count("||||") == 1:
                        listUnling = listUnling.replace("List of unlings: ", "")
                        listUnling = listUnling.replace("||||", "")
                        listUnlingData = listUnling.split("//")
                        print("listUnling Splitted : ")
                        print(listUnlingData)
                        datalistUnling = listUnlingData[1].split("||")
                        listUnlingData[0] = listUnlingData[0].strip()
                        if not listUnlingData[0] == "":
                            for row in datalistUnling:
                                userAdminName = row.strip()
                                if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                    if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName,
                                                                                                listUnlingData[0]):
                                        countReAdded = countReAdded + 1
                                        print("Count + 1: " + str(countReAdded))
                                        removeAdminRoleWhileSetNew(userAdminName)
                                        addAdminRole(userAdminName, listUnlingData[0])
                                    elif not checkIfAdminHaveRole(userAdminName, listUnlingData[0]):
                                        countAdded = countAdded + 1
                                        print("Count + 1: " + str(countAdded))
                                        addAdminRole(userAdminName, listUnlingData[0])
                        listUnlingAdding = False
                        continue
                    else:
                        listUnlingAdded = row.replace("\n", "")
                        print("listUnling added: " + listUnlingAdded)
                        if listUnling != listUnlingAdded:
                            listUnling += listUnlingAdded
                        print("Added row listUnling: " + listUnling)
                        if listUnling.count("||||") == 1:
                            listUnling = listUnling.replace("List of unlings: ", "")
                            listUnling = listUnling.replace("||||", "")
                            listUnlingData = listUnling.split("//")
                            print("listUnling Splitted : ")
                            print(listUnlingData)
                            datalistUnling = listUnlingData[1].split("||")
                            listUnlingData[0] = listUnlingData[0].strip()
                            if not listUnlingData[0] == "":
                                for row in datalistUnling:
                                    userAdminName = row.strip()
                                    if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                        if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName,
                                                                                                    listUnlingData[0]):
                                            countReAdded = countReAdded + 1
                                            print("Count + 1: " + str(countReAdded))
                                            removeAdminRoleWhileSetNew(userAdminName)
                                            addAdminRole(userAdminName, listUnlingData[0])
                                        elif not checkIfAdminHaveRole(userAdminName, listUnlingData[0]):
                                            countAdded = countAdded + 1
                                            print("Count + 1: " + str(countAdded))
                                            addAdminRole(userAdminName, listUnlingData[0])
                            listUnlingAdding = False
                            continue
                        else:
                            listUnlingAdding = True
                            continue
                else:
                    print("Other RoleAdmins row: " + row)
                    continue
        countAdded = 0
        for row in lines:
            print("New Padavan loop ================= " + "Number of added: " + str(
                countAdded) + "; Number of readded: " + str(
                    countReAdded) + "; Number |||| " + str(listPadavan.count("||||")))
            if "Падаван" in row:
                listPadavan = row.replace("\n", "")
                print("New Padavan row: " + listPadavan)
                listPadavanAdding = True
            if listPadavanAdding:
                if listPadavan.count("||||") == 1:
                    listPadavan = listPadavan.replace("List of Padavans: ", "")
                    listPadavan = listPadavan.replace("||||", "")
                    listPadavanData = listPadavan.split("//")
                    print("listPadavan Splitted : ")
                    print(listPadavanData)
                    datalistPadavan = listPadavanData[1].split("||")
                    listPadavanData[0] = listPadavanData[0].strip()
                    if not listPadavanData[0] == "":
                        for row in datalistPadavan:
                            userAdminName = row.strip()
                            if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName, listPadavanData[0]):
                                    countReAdded = countReAdded + 1
                                    print("Count + 1: " + str(countReAdded))
                                    removeAdminRoleWhileSetNew(userAdminName)
                                    addAdminRole(userAdminName, listPadavanData[0])
                                elif not checkIfAdminHaveRole(userAdminName, listPadavanData[0]):
                                    countAdded = countAdded + 1
                                    print("Count + 1: " + str(countAdded))
                                    addAdminRole(userAdminName, listPadavanData[0])
                    listPadavanAdding = False
                    continue
                else:
                    listPadavanAdded = row.replace("\n", "")
                    print("listPadavan added: " + listPadavanAdded)
                    if listPadavan != listPadavanAdded:
                        listPadavan += listPadavanAdded
                    print("Added row listPadavans: " + listPadavan)
                    if listPadavan.count("||||") == 1:
                        listPadavan = listPadavan.replace("List of Padavans: ", "")
                        listPadavan = listPadavan.replace("||||", "")
                        listPadavanData = listPadavan.split("//")
                        print("listPadavan Splitted : ")
                        print(listPadavanData)
                        datalistPadavan = listPadavanData[1].split("||")
                        listPadavanData[0] = listPadavanData[0].strip()
                        if not listPadavanData[0] == "":
                            for row in datalistPadavan:
                                userAdminName = row.strip()
                                if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                    if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName,
                                                                                                listPadavanData[0]):
                                        countReAdded = countReAdded + 1
                                        print("Count + 1: " + str(countReAdded))
                                        removeAdminRoleWhileSetNew(userAdminName)
                                        addAdminRole(userAdminName, listPadavanData[0])
                                    elif not checkIfAdminHaveRole(userAdminName, listPadavanData[0]):
                                        countAdded = countAdded + 1
                                        print("Count + 1: " + str(countAdded))
                                        addAdminRole(userAdminName, listPadavanData[0])
                        listPadavanAdding = False
                        continue
                    else:
                        listPadavanAdding = True
                        continue
            else:
                print("Other RoleAdmins row: " + row)
                continue
        countAdded = 0
        for row in lines:
            print("New KnigtJedi loop ================= " + "Number of added: " + str(
                countAdded) + "; Number of readded: " + str(
                    countReAdded) + "; Number |||| " + str(listKnigtJedi.count("||||")))
            if "Лицар-джедай" in row:
                listKnigtJedi = row.replace("\n", "")
                print("New KnigtJedi row: " + listKnigtJedi)
                listKnigtJediAdding = True
            if listKnigtJediAdding:
                if listKnigtJedi.count("||||") == 1:
                    listKnigtJedi = listKnigtJedi.replace("List of Knigt Jedis: ", "")
                    listKnigtJedi = listKnigtJedi.replace("||||", "")
                    listKnigtJediData = listKnigtJedi.split("//")
                    print("listKnigtJedi Splitted : ")
                    print(listKnigtJediData)
                    datalistKnigtJedi = listKnigtJediData[1].split("||")
                    listKnigtJediData[0] = listKnigtJediData[0].strip()
                    if not listKnigtJediData[0] == "":
                        for row in datalistKnigtJedi:
                            userAdminName = row.strip()
                            if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName, listKnigtJediData[0]):
                                    countReAdded = countReAdded + 1
                                    print("Count + 1: " + str(countReAdded))
                                    removeAdminRoleWhileSetNew(userAdminName)
                                    addAdminRole(userAdminName, listKnigtJediData[0])
                                elif not checkIfAdminHaveRole(userAdminName, listKnigtJediData[0]):
                                    countAdded = countAdded + 1
                                    print("Count + 1: " + str(countAdded))
                                    addAdminRole(userAdminName, listKnigtJediData[0])
                    listKnigtJediAdding = False
                    continue
                else:
                    listKnigtJediAdded = row.replace("\n", "")
                    print("listKnigtJedi added: " + listKnigtJediAdded)
                    if listKnigtJedi != listKnigtJediAdded:
                        listKnigtJedi += listKnigtJediAdded
                    print("Added row listKnigtJedis: " + listKnigtJedi)
                    if listKnigtJedi.count("||||") == 1:
                        listKnigtJedi = listKnigtJedi.replace("List of Knigt Jedis: ", "")
                        listKnigtJedi = listKnigtJedi.replace("||||", "")
                        listKnigtJediData = listKnigtJedi.split("//")
                        print("listKnigtJedi Splitted : ")
                        print(listKnigtJediData)
                        datalistKnigtJedi = listKnigtJediData[1].split("||")
                        listKnigtJediData[0] = listKnigtJediData[0].strip()
                        if not listKnigtJediData[0] == "":
                            for row in datalistKnigtJedi:
                                userAdminName = row.strip()
                                if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                    if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName,
                                                                                                listKnigtJediData[0]):
                                        countReAdded = countReAdded + 1
                                        print("Count + 1: " + str(countReAdded))
                                        removeAdminRoleWhileSetNew(userAdminName)
                                        addAdminRole(userAdminName, listKnigtJediData[0])
                                    elif not checkIfAdminHaveRole(userAdminName, listKnigtJediData[0]):
                                        countAdded = countAdded + 1
                                        print("Count + 1: " + str(countAdded))
                                        addAdminRole(userAdminName, listKnigtJediData[0])
                        listKnigtJediAdding = False
                        continue
                    else:
                        listKnigtJediAdding = True
                        continue
            else:
                print("Other RoleAdmins row: " + row)
                continue
        countAdded = 0
        for row in lines:
            print("New GrandMaster loop ================= " + "Number of added: " + str(
                countAdded) + "; Number of readded: " + str(
                    countReAdded) + "; Number |||| " + str(listGrandMaster.count("||||")))
            if "гранд-майстер Ордена джедаїв" in row:
                listGrandMaster = row.replace("\n", "")
                print("New GrandMaster row: " + listGrandMaster)
                listGrandMasterAdding = True
            if listGrandMasterAdding:
                if listGrandMaster.count("||||") == 1:
                    listGrandMaster = listGrandMaster.replace("List of GrandMasters: ", "")
                    listGrandMaster = listGrandMaster.replace("||||", "")
                    listGrandMasterData = listGrandMaster.split("//")
                    print("listGrandMaster Splitted : ")
                    print(listGrandMasterData)
                    datalistGrandMaster = listGrandMasterData[1].split("||")
                    listGrandMasterData[0] = listGrandMasterData[0].strip()
                    if not listGrandMasterData[0] == "":
                        for row in datalistGrandMaster:
                            userAdminName = row.strip()
                            if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName,
                                                                                  listGrandMasterData[0]):
                                    countReAdded = countReAdded + 1
                                    print("Count + 1: " + str(countReAdded))
                                    removeAdminRoleWhileSetNew(userAdminName)
                                    addAdminRole(userAdminName, listGrandMasterData[0])
                                elif not checkIfAdminHaveRole(userAdminName, listGrandMasterData[0]):
                                    countAdded = countAdded + 1
                                    print("Count + 1: " + str(countAdded))
                                    addAdminRole(userAdminName, listGrandMasterData[0])
                    listGrandMasterAdding = False
                    continue
                else:
                    listGrandMasterAdded = row.replace("\n", "")
                    print("listGrandMaster added: " + listGrandMasterAdded)
                    if listGrandMaster != listGrandMasterAdded:
                        listGrandMaster += listGrandMasterAdded
                    print("Added row GrandMasters: " + listGrandMaster)
                    if listGrandMaster.count("||||") == 1:
                        listGrandMaster = listGrandMaster.replace("List of GrandMasters: ", "")
                        listGrandMaster = listGrandMaster.replace("||||", "")
                        listGrandMasterData = listGrandMaster.split("//")
                        print("listGrandMaster Splitted : ")
                        print(listGrandMasterData)
                        datalistGrandMaster = listGrandMasterData[1].split("||")
                        listGrandMasterData[0] = listGrandMasterData[0].strip()
                        if not listGrandMasterData[0] == "":
                            for row in datalistGrandMaster:
                                userAdminName = row.strip()
                                if not userAdminName == "" and not checkIfAdminHaveRole(userAdminName, roleName[3]):
                                    if checkIfAdmin(userAdminName) and not checkIfAdminHaveRole(userAdminName,
                                                                                                listGrandMasterData[0]):
                                        countReAdded = countReAdded + 1
                                        print("Count + 1: " + str(countReAdded))
                                        removeAdminRoleWhileSetNew(userAdminName)
                                        addAdminRole(userAdminName, listGrandMasterData[0])
                                    elif not checkIfAdminHaveRole(userAdminName, listGrandMasterData[0]):
                                        countAdded = countAdded + 1
                                        print("Count + 1: " + str(countAdded))
                                        addAdminRole(userAdminName, listGrandMasterData[0])
                        listGrandMasterAdding = False
                        continue
                    else:
                        listGrandMasterAdding = True
                        continue
            else:
                print("Other RoleAdmins row: " + row)
                continue
        countAdded = 0
        for row in lines:
                print("New Listadmins loop ================= " + "Number of added: " + str(countAdded) + "; Number |||| " + str(listAdmins.count("||||")))
                if "List of admins: " in row:
                    listAdmins = row.replace("\n", "")
                    print("New ListAdmins row: " + listAdmins)
                    listadminsAdding = True
                if listadminsAdding:
                    if listAdmins.count("||||") == 1:
                        listAdmins = listAdmins.replace("List of admins: ", "")
                        listAdmins = listAdmins.replace("||||", "")
                        listAdminsData = listAdmins.split("||")
                        print("listAdmins Splitted : ")
                        print(listAdminsData)
                        for row in listAdminsData:
                            datarow = row.strip()
                            if not datarow == "":
                                data = datarow.split("~")
                                data[0] = data[0].strip()
                                data[1] = data[1].strip()
                                if not data[0] == "" and not data[1] == "":
                                    if not checkIfAdmin(data[0]):
                                        countAdded = countAdded + 1
                                        print("Count + 1: " + str(countAdded))
                                        addAdminToDb(data[0], data[1])
                        listadminsAdding = False
                        continue
                    else:
                        listAdminsAdded = row.replace("\n", "")
                        print("listAdmins added: " + listAdminsAdded)
                        if listAdmins != listAdminsAdded:
                            listAdmins += listAdminsAdded
                        print("Added row listAdmins: " + listAdmins)
                        if listAdmins.count("||||") == 1:
                            listAdmins = listAdmins.replace("List of admins: ", "")
                            listAdmins = listAdmins.replace("||||", "")
                            listAdminsData = listAdmins.split("||")
                            print("listAdmins Splitted : ")
                            print(listAdminsData)
                            for row in listAdminsData:
                                datarow = row.strip()
                                if not datarow == "":
                                    data = datarow.split("~")
                                    data[0] = data[0].strip()
                                    data[1] = data[1].strip()
                                    if not data[0] == "" and not data[1] == "":
                                        if not checkIfAdmin(data[0]):
                                            countAdded = countAdded + 1
                                            print("Count + 1: " + str(countAdded))
                                            addAdminToDb(data[0], data[1])
                            listadminsAdding = False
                            continue
                        else:
                            listadminsAdding = True
                            continue
                else:
                    print("RoleAdmins row: " + row)
                    continue
                # else:
                #     roleLine = row.replace("\n", "")
                #     roleLine = roleLine.split("/")
                #     print("Roleline: ")
                #     print(roleLine)
                #     role = roleLine[0]
                #     listAdmins = roleLine[1].split(";")
                #     print("ListAdmins:: ")
                #     print(listAdmins)
                #     for admin in listAdmins:
                #         if not checkIfAdminHaveRole(admin, role) and not admin == "":
                #             countAdded = countAdded + 1
                #             print("admin:" + admin)
                #             addAdminRole(admin, role)
        # except:
        #     msg = bot.reply_to(message, "Отакої, щось трапилось не так, пришліть текстовий файл ще раз!")
        #     bot.register_next_step_handler(msg, handle_document_admin, username)
    if countAdded == 0 and countReAdded == 0:
        bot.reply_to(message, "Процес завершено, нових адміністраторів не виявлено!", reply_markup=types.ReplyKeyboardRemove())
    elif countAdded > 0 or countReAdded > 0:
        bot.reply_to(message, "Адміністратори успішно затягнуті!", reply_markup=types.ReplyKeyboardRemove())


def proccesDocumentAnegdot(message, username):
    countAdded = 0
    with open("listAnegdotsProcces.txt", 'r', encoding='utf-8') as fileAnegdot:
        lines = fileAnegdot.readlines()
        try:
            anegdot = ""
            category = ""
            categoryAdding = False
            anegdotAdding = False
            for row in lines:
                print("New Category loop ================= " + "Number of added: " + str(countAdded))
                if "Category: " in row:
                    # category = row.replace("\n", "")
                    category = row
                    print("New row category: " + category)
                    categoryAdding = True
                if categoryAdding:
                    if category.count("||||") == 1 and category.count("Category: ") == 1:
                        category = category.replace("Category: ", "")
                        category = category.replace("||||", "")
                        categoryData = category.split("||")
                        categoryData[2] = categoryData[2].replace("\n", "")
                        categoryData[0] = categoryData[0].strip(" ")
                        categoryData[1] = categoryData[1].strip(" ")
                        categoryData[2] = categoryData[2].strip(" ")
                        print("Category Splitted : ")
                        print(categoryData)
                        if not checkIfExistsCategory(categoryData[0]) and not categoryData[0] == "" and not \
                        categoryData[1] == "" and not categoryData[2] == "":
                            countAdded = countAdded + 1
                            print("Count + 1: " + str(countAdded))
                            # datadate = categoryData[2].replace("\n", "")
                            addCategoryUsingTxt(categoryData[0], categoryData[1], categoryData[2])
                        categoryAdding = False
                        continue
                    else:
                        # categoryadded = row.replace("\n", "")
                        categoryadded = row
                        print("Category added: " + categoryadded)
                        if category != categoryadded:
                            category += categoryadded
                        print("Added row category: " + category)
                        if category.count("||||") == 1 and category.count("Category: ") == 1:
                            category = category.replace("Category: ", "")
                            category = category.replace("||||", "")
                            categoryData = category.split("||")
                            categoryData[2] = categoryData[2].replace("\n", "")
                            categoryData[0] = categoryData[0].strip(" ")
                            categoryData[1] = categoryData[1].strip(" ")
                            categoryData[2] = categoryData[2].strip(" ")
                            print("Category Splitted : ")
                            print(categoryData)
                            if not checkIfExistsCategory(categoryData[0]) and not categoryData[0] == "" and not categoryData[1] == "" and not categoryData[2] == "":
                                countAdded = countAdded + 1
                                print("Count + 1: " + str(countAdded))
                                # datadate = categoryData[2].replace("\n", "")
                                addCategoryUsingTxt(categoryData[0], categoryData[1], categoryData[2])
                            categoryAdding = False
                            continue
                        else:
                            categoryAdding = True
                            continue
                else:
                    print("Anegdot row: " + row)
                    continue
            for row in lines:
                print("New Anegdot loop =================" + "Number of added: " + str(countAdded))
                if "Anegdot: " in row:
                    # anegdot = row.replace("\n", "")
                    anegdot = row
                    print("New row anegdot: " + anegdot)
                    anegdotAdding = True
                if anegdotAdding:
                    if anegdot.count("||||") == 1 and anegdot.count("Anegdot: ") == 1:
                        anegdot = anegdot.replace("Anegdot: ", "")
                        anegdot = anegdot.replace("||||", "")
                        anegdotData = anegdot.split("||")
                        anegdotData[3] = anegdotData[3].replace("\n", "")
                        anegdotData[0] = anegdotData[0].strip()
                        anegdotData[1] = anegdotData[1].strip()
                        anegdotData[2] = anegdotData[2].strip()
                        anegdotData[3] = anegdotData[3].strip()
                        print("Anegdot Splitted : ")
                        print(anegdotData)
                        if not checkIfExistsAnedgot(anegdotData[0], anegdotData[1]) and not anegdotData[0] == "" and not anegdotData[1] == "" and not anegdotData[2] == "" and not anegdotData[3] == "":
                            countAdded = countAdded + 1
                            print("Count + 1: " + str(countAdded))
                            addAnegdotToDbUsingTxt(anegdotData[0], anegdotData[1], anegdotData[2], anegdotData[3])
                        anegdotAdding = False
                        continue
                    else:
                        # anegdotadded = row.replace("\n", "")
                        anegdotadded = row
                        print("Anegdot added: " + anegdotadded)
                        if anegdot != anegdotadded:
                            anegdot += anegdotadded
                            print("Added row anegdot: " + anegdot)
                        if anegdot.count("||||") == 1 and anegdot.count("Anegdot: ") == 1:
                            anegdot = anegdot.replace("Anegdot: ", "")
                            anegdot = anegdot.replace("||||", "")
                            anegdotData = anegdot.split("||")
                            anegdotData[3] = anegdotData[3].replace("\n", "")
                            anegdotData[0] = anegdotData[0].strip()
                            anegdotData[1] = anegdotData[1].strip()
                            anegdotData[2] = anegdotData[2].strip()
                            anegdotData[3] = anegdotData[3].strip()
                            print("Anegdot Splitted : ")
                            print(anegdotData)
                            if not checkIfExistsAnedgot(anegdotData[0], anegdotData[1]) and not anegdotData[
                                                                                                    0] == "" and not \
                            anegdotData[1] == "" and not anegdotData[2] == "" and not anegdotData[3] == "":
                                countAdded = countAdded + 1
                                print("Count + 1: " + str(countAdded))
                                addAnegdotToDbUsingTxt(anegdotData[0], anegdotData[1], anegdotData[2], anegdotData[3])
                            anegdotAdding = False
                            continue
                        else:
                            anegdotAdding = True
                            continue
                else:
                    print("Category row: " + row)
                    continue
        except:
            msg = bot.reply_to(message, "Отакої, щось трапилось не так, пришліть текстовий файл ще раз!")
            bot.register_next_step_handler(msg, handle_document_admin, username)
    if countAdded == 0:
        bot.reply_to(message, "Процес завершено, нових категорій або анекдотів не виявлено!", reply_markup=types.ReplyKeyboardRemove())
    elif countAdded > 0:
        bot.reply_to(message, "Категорії та анекдоти успішно затягнуті!", reply_markup=types.ReplyKeyboardRemove())



@bot.message_handler(commands=['gettxtadmins'])
def gettxtadmins(message):
    private_chat_id = message.from_user.id
    if checkIfAdmin(str(message.from_user.username)):
        adminRights = str(GetAdminRights(message.from_user.username))
        if listJediKnightRights in adminRights:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Для перегляду")
            item2 = types.KeyboardButton("Для бази даних")
            item3 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1, item2)
            markup.row(item3)
            msg = bot.send_message(private_chat_id, "Для чого вам потрібен файл", reply_markup=markup)
            bot.register_next_step_handler(msg, gettxtfileadmin, message.from_user.username)


def gettxtfileadmin(message, username):
    if message.from_user.username == username:
        with open('listAnegdots.txt', 'w', encoding='utf-8') as f:
            info = ""
            if message.text == "Для перегляду":
                with open('listAdmins.txt', 'w', encoding='utf-8') as f:
                    info = ""
                    info += "List of admins: \n\n"
                    for row in GetListAndWhoAddOfAdmins():
                        row = row.split("~")
                        info += "UserName: " + row[0] + " | Who Added: " + row[1]
                        info += " | "
                        info += "Role: " + GetRole(row[0]) + "\n\n"
                        # print(info)
                    f.write(info)
                bot.send_document(message.from_user.id, open(r'listAdmins.txt', 'rb'), reply_markup=types.ReplyKeyboardRemove())
            elif message.text == "Для бази даних":
                with open('listAdmins.txt', 'w', encoding='utf-8') as f:
                    info = ""
                    info += "List of admins: "
                    for row in GetListAndWhoAddOfAdmins():
                        info += row + "||"
                    info += "||\n"
                    for row in GetRoleAdminsAll():
                        info += row[1] + "//" + row[2] + "//" + row[3] + "||||\n"
                    f.write(info)
                bot.send_document(message.from_user.id, open(r'listAdmins.txt', 'rb'), reply_markup=types.ReplyKeyboardRemove())
            elif message.text == "🛑 Відмінити операцію!":
                farewell = getFarewellAccoringToHours()
                print(farewell)
                bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.register_next_step_handler(message, gettxtfileadmin, username)


@bot.message_handler(commands=['addcategory'])
def addcategory(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            adminRights = str(GetAdminRights(message.from_user.username))
            if listUnlingRights in adminRights:
                AddChat(message)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                markup.row(item1)
                bot.reply_to(message, "Введіть назву категорії", reply_markup=markup)
                bot.register_next_step_handler(message, registerCategory, message.from_user.username)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


def registerCategory(message, username):
    maxNumOfSymsForCategory = 55
    stringbyte = "showane: " + message.text
    print("Bytes Message.text: " + str(len(message.text.encode('utf-8'))))
    print("Bytes stringbyte: " + str(len(stringbyte.encode('utf-8'))))
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif len(message.text.encode('utf-8')) <= maxNumOfSymsForCategory:
            if checkIfExistsCategory(str(message.text)):
                msg = bot.reply_to(message, "Категорія уже існує, спробуйте надіслати щось нове!")
                bot.register_next_step_handler(msg, registerCategory, username)
            else:
                addCategory(message)
                bot.reply_to(message, "Категорію успішно додано", reply_markup=types.ReplyKeyboardRemove())
            markup = InlineKeyboardMarkup()
            markup.width = 3
            for row in getCategories():
                markup.add(InlineKeyboardButton(row, callback_data="showane: " + row))
            bot.reply_to(message, "Список категорій", reply_markup=markup)
        else:
            msg = bot.reply_to(message, f'Назва категорії: "{message.text}" є занадто довгою ( максимальна кількість символів: ( 55 - для латиниці, 27 - для кирилиці) )')
            bot.register_next_step_handler(msg, registerCategory, username)
    else:
        bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(message, registerCategory, username)


@bot.message_handler(commands=['addanegdot'])
def addanegdot(message):
    rights = 0
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            adminRights = str(GetAdminRights(message.from_user.username))
            if listUnlingRights in adminRights:
                AddChat(message)
                if checkIfNotExistCategories():
                    bot.reply_to(message,
                                 "Ви ще не додали категорій, до яких ви будете додавати анекдоти,тому введіть команду /addcategory")
                else:
                    markup = InlineKeyboardMarkup()
                    markup.width = 3
                    for row in getCategories():
                        print(row)
                        markup.add(InlineKeyboardButton(row,
                                                        callback_data="addaneg: " + row))
                    bot.reply_to(message, "Оберіть категорію, до якої буде відноситися анегдот", reply_markup=markup)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.message_handler(commands=['deleteanegdot'])
def removeanegdot(message):
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            adminRights = str(GetAdminRights(message.from_user.username))
            if listPadavanRights in adminRights:
                AddChat(message)
                deleteNoneAnegdots()
                if not checkIfNotExistAnedgots():
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                    markup.row(item1)
                    msg = bot.reply_to(message, "Впишіть анекдот, який хочете видалити", reply_markup=markup)
                    bot.register_next_step_handler(msg, removeanegdotfunc, message.from_user.username)
                else:
                    bot.reply_to(message,
                                 "На жаль, ще не було додано жодного анекдота. Щоб додати - використайте команду /addanegdot")
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
                                     callback_data="chorand: " + "readanegdotbycategory")
        item2 = InlineKeyboardButton(text="Почитати анекдот",
                                     callback_data="chorand: " + "readanegdot")
        markup.add(item1, item2)
        bot.reply_to(message, 'Оберіть один із варіантів.', reply_markup=markup)


@bot.message_handler(commands=['deletecategory'])
def deletecategory(message):
    rights = 0
    if checkIfNoneUserName(message.from_user.username):
        bot.reply_to(message, "Для початку створіть собі username.")
    else:
        if checkIfAdmin(str(message.from_user.username)):
            adminRights = str(GetAdminRights(message.from_user.username))
            print("AdminRights: " + adminRights)
            if listPadavanRights in adminRights:
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
                                                        callback_data="adelcat: " + row))
                    bot.reply_to(message, "Список категорій", reply_markup=markup)
        else:
            bot.reply_to(message, "У вас немає прав на цю дію!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("adelcat: "))
def callback_query(call: types.CallbackQuery):
    if checkIfAdmin(str(call.from_user.username)):
        print(call.from_user.username)
        category = str(call.data).replace("adelcat: ", "")
        # print("Text: " + call.data)
        # info = info.split(splitword_one)
        # username = info[0]
        # category = info[1]
        # if username == call.from_user.username:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Так ✅")
        item2 = types.KeyboardButton("Ні ⛔")
        markup.row(item1, item2)
        # item1 = InlineKeyboardButton(text="Так ✅",
        #                                  callback_data="delcate: " + call.from_user.username + splitword_one + category)
        # item2 = InlineKeyboardButton(text="Ні ⛔",
        #                                  callback_data="endoper: " + call.from_user.username)
        # markup.add(item1, item2)
        msg = bot.reply_to(call.message,
                           'Ви впевнені, що хочете видалити категорію та анекдоти, які відносяться до неї?.',
                           reply_markup=markup)
        bot.register_next_step_handler(msg, delcategory, category, call.from_user.username)
        # else:
        #     bot.reply_to(call.message, f"Зараз черга @{username}.")
    else:
        print(f'{call.from_user.username} is not an admin')


# @bot.callback_query_handler(func=lambda call: call.data.startswith("delcate: "))
# def callback_query(call: types.CallbackQuery):
def delcategory(message, category, username):
    # print(call.from_user.username)
    # info = str(call.data).replace("delcate: ","")
    # info = info.split(splitword_one)
    # username = info[0]
    # category = info[1]
    # if username == call.from_user.username:
    if username == message.from_user.username:
        if message.text == "Так ✅":
            if checkIfExistsCategory(category):
                deleteAnegdotsByCategory(category)
                deleteCategory(category)
                bot.reply_to(message, "Категорію та анекдоти з неї успішно видалено", reply_markup = types.ReplyKeyboardRemove())
            else:
                bot.reply_to(message, "Такої категорії не існує", reply_markup = types.ReplyKeyboardRemove())
        elif message.text == "Ні ⛔":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup = types.ReplyKeyboardRemove())
        else:
            bot.register_next_step_handler(message, delcategory, category, username)
    else:
        msg = bot.reply_to(message, f"Зараз черга @{username}.")
        bot.register_next_step_handler(msg, delcategory, category, username)


# @bot.callback_query_handler(func=lambda call: call.data.startswith("endoper: "))
# def callback_query(call: types.CallbackQuery):
#     print(call.from_user.username)
#     username = str(call.data).replace("endoper: ","")
#     if username == call.from_user.username:
#             farewell = getFarewellAccoringToHours()
#             print(farewell)
#             bot.reply_to(call.message, farewell)
#     else:
#         bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("addaneg: "))
def callback_query(call: types.CallbackQuery):
    if checkIfAdmin(str(call.from_user.username)):
        category = str(call.data).replace("addaneg: ", "")
        # info = info.split(splitword_one)
        # username = info[0]
        # category = info[1]
        # if username == call.from_user.username:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("🛑 Відмінити операцію!")
        markup.row(item1)
        msg = bot.reply_to(call.message, "Впишіть ваш анекдот", reply_markup=markup)
        bot.register_next_step_handler(msg, addAnegdot, category, call.from_user.username)
        # else:
        #     bot.reply_to(call.message, f"Зараз черга @{username}.")
    else:
        print(f'{call.from_user.username} is not an admin')




@bot.callback_query_handler(func=lambda call: call.data.startswith("chorand: "))
def callback_query(call: types.CallbackQuery):
    answer = str(call.data).replace("chorand: ","")
    # info = info.split(splitword_one)
    # username = info[0]
    # answer = info[1]
    # print(info)
    # print(call.from_user.username)
    # if username == call.from_user.username:
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
                markup.add(InlineKeyboardButton(row, callback_data="randane: " + row))
            bot.reply_to(call.message, "Оберіть категорію анекдота", reply_markup=markup)
    elif answer == "readanegdot":
        if checkIfNotExistAnedgots():
            bot.reply_to(call.message, "Ви ще не додали анекдотів")
        else:
            bot.reply_to(call.message, getAnegdot())
    # else:
    #     bot.reply_to(call.message, f"Зараз черга @{username}.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("randane: "))
def callback_query(call: types.CallbackQuery):
    category = str(call.data).replace("randane: ", "")
    # info = info.split(splitword_one)
    # username = info[0]
    # category = info[1]
    # if username == call.from_user.username:
    if checkIfNotExistAnedgotsByCategory(category):
        bot.reply_to(call.message, "Ви ще не додали анекдотів для цієї категорії")
    else:
        bot.reply_to(call.message, getRandomAnegdotByCategory(category))
    # else:
    #     bot.reply_to(call.message, f"Зараз черга @{username}.")



def addAnegdot(message, category, username):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif len(str(message.text)) <= maxNumOfSymsForAnegdot:
            if checkIfExistsAnedgot(category, str(message.text)):
                msg = bot.reply_to(message, "Анекдот уже існує, спробуйте надіслати щось нове!")
                bot.register_next_step_handler(msg, addAnegdot, category, username)
            else:
                addAnegdotToDb(message, category)
                bot.reply_to(message, "Анекдот успішно доданий!", reply_markup=types.ReplyKeyboardRemove())
        else:
            msg = bot.reply_to(message, "Ви перевищили ліміт символів ( максимальна кількість - 510 ), спробуйте ще раз!")
            bot.register_next_step_handler(msg, addAnegdot, category, username)
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


def send_meme():
    if checkIfExistChats():
        deleteNoneAnegdots()
        listId = GetChatsId()
        print(listId)
        for row in listId:
            try:
                bot.send_video(chat_id=row, video=open('video_2022-09-17_00-39-43.mp4', 'rb'), caption='Інфа наступна')
                # bot.send_photo(chat_id=row, photo=open('150359_main.jpg', 'rb'))
                # bot.send_photo(chat_id=row, photo=open('150362_main.jpg', 'rb'))
            except:
                DeleteChat(row)


def yogurt():
    if checkIfExistChats():
        deleteNoneAnegdots()
        listId = GetChatsId()
        print(listId)
        for row in listId:
            try:
                bot.send_message(row, "По йогурту 🥛 і спать.")
            except:
                DeleteChat(row)


def balls():
    if checkIfExistChats():
        deleteNoneAnegdots()
        listId = GetChatsId()
        print(listId)
        for row in listId:
            try:
                bot.send_photo(chat_id=row, photo=open('photo_2022-09-06_16-30-43.jpg', 'rb'))
            except:
                DeleteChat(row)


# @server.route('/' + TOKEN, methods=['POST'])
# def getMessage():
#     json_string = request.get_data().decode('utf-8')
#     update = telebot.types.Update.de_json(json_string)
#     bot.process_new_updates([update])
#     return "!", 200
#
#
# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://cryptic-sea-86814.herokuapp.com/' + TOKEN)
#     return "!", 200

def main():
    print('Бот Стартує!!!')
    try:
        bot.infinity_polling()
    except:
        print("Not today")


if __name__ == "__main__":
    main()
    # server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
