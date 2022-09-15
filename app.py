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
splitword_one = '@;'
splitword_two = '@38)89'
roleName = ['Юнлінг', 'Падаван', 'Лицар-джедай', 'гранд-майстер Ордена джедаїв']
listRights = ['addcategory', 'addanegdot', 'deletecategory', 'deleteanegdot', 'gettxtanegdot', 'gettxtadmins', 'controladmin', 'inserttxtcategoriesandanegdotstodb', 'inserttxtadminstodb']
listUnlingRights = listRights[0] + ";" + listRights[1]
listPadavanRights = listUnlingRights + ";" + listRights[2] + ";" + listRights[3]
listJediKnightRights = listPadavanRights + ";" + listRights[4] + ";" + listRights[5]
listGrandMasterRights = listJediKnightRights + ";" + listRights[6] + ";" + listRights[7] + ";" + listRights[8]


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
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item1 = types.KeyboardButton("🛑 Відмінити операцію!")
                markup.row(item1)
                msg = bot.reply_to(message, "Введіть username кандидата, для того щоб увійти в панель управління адміністрацією.", reply_markup = markup)
                bot.register_next_step_handler(msg, controlAdminPanel, message.from_user.username)


def controlAdminPanel(message, username):
    if username == message.from_user.username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        elif message.text is None:
            msg = bot.reply_to(message, f'Я був би не проти нюдсів блонд, але пришліть будь ласка мені username')
            bot.register_next_step_handler(msg, controlAdminPanel, username)
        else:
            newAdminUsername = str(message.text)
            markup = InlineKeyboardMarkup()
            markup.width = 3
            markup.add(InlineKeyboardButton(f'Додати {message.text} до адміністраторів?',
                                            callback_data="addadmin: " + newAdminUsername))
            markup.add(InlineKeyboardButton(f'Забрати {message.text}  адміністраторські права?',
                                            callback_data="remoadm: " + newAdminUsername))
            bot.reply_to(message, "Оберіть один з варіантів", reply_markup=markup)
    else:
        msg = bot.reply_to(message,f'Зараз черга {username}')
        bot.register_next_step_handler(msg, controlAdminPanel, username)


@bot.callback_query_handler(func=lambda call: call.data.startswith("addadmin: "))
def callback_query(call: types.CallbackQuery):
    if checkIfAdmin(str(call.from_user.username)):
        newAdminUserName = str(call.data).replace("addadmin: ", "")
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
        if deleteAdminUserName == "@kreager" and call.from_user.username == "kreager":
            msg = bot.reply_to(call.message,"Гранд-Майстре, якщо ви хочете себе вбити, то скажіть @alexagranv ще раз, що вона вам подобається.")
            bot.register_next_step_handler(msg, controlAdminPanel, call.from_user.username)
        elif deleteAdminUserName == "@kreager":
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
            msg = bot.reply_to(message, f"Адміна {deleteAdminUserName} з такою роллю {role} не існує.", reply_markup=types.ReplyKeyboardRemove())
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
                    info += "Category: " + row[1] + ";" + row[3] + ";" + row[4]
                    # info += " Time, when added: " + row[4]
                    info += "\n"
                    for row in getFullInfoAnegdotsByCategory(row[1]):
                        info += "Anegdot: " + row[1] + ";" + row[3] + ";" + row[5] + ";" + row[6]
                        info += "\n"
            elif message.text == "🛑 Відмінити операцію!":
                farewell = getFarewellAccoringToHours()
                print(farewell)
                bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.register_next_step_handler(message, gettxtfileanegdot, username)
            print(info)
            f.write(info)
        bot.send_document(message.from_user.id, open(r'listAnegdots.txt', 'rb'), reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['inserttxtanegdottodb'])
def inserttxtanegdottodb(message):
    if checkIfAdmin(str(message.from_user.username)):
        adminRights = str(GetAdminRights(message.from_user.username))
        if listGrandMasterRights in adminRights:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("🛑 Відмінити операцію!")
            markup.row(item1)
            private_chat_id = message.from_user.id
            msg = bot.send_message(private_chat_id, "Пришліть текстовий файл з анекдотами", reply_markup=markup)
            bot.register_next_step_handler(msg,handle_document_anegdot,message.from_user.username)


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
                    print(downloaded_file)
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
            msg = bot.send_message(private_chat_id, "Пришліть текстовий файл зі списком адмінів")
            bot.register_next_step_handler(msg,handle_document_admin, message.from_user.username)


def handle_document_admin(message, username):
    if message.from_user.username == username:
        if message.text == "🛑 Відмінити операцію!":
            farewell = getFarewellAccoringToHours()
            print(farewell)
            bot.reply_to(message, farewell, reply_markup=types.ReplyKeyboardRemove())
        else:
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                with open("listAdminsProcces.txt", 'wb') as new_file:
                    # print(downloaded_file)
                    new_file.write(downloaded_file)
                proccesDocumentAdmin(message, username)
            except:
                msg = bot.reply_to(message, "Пришліть будь ласка текстовий файл!")
                bot.register_next_step_handler(msg, handle_document_admin, username)


def proccesDocumentAdmin(message, username):
    countAdded = 0
    with open("listAdminsProcces.txt", 'r', encoding="utf8") as fileAdmin:
        lines = fileAdmin.readlines()
        try:
            for row in lines:
                if "List of admins: " in row:
                    listAdmins = row.replace("\n", "")
                    listAdmins = listAdmins.replace("List of admins: ", "")
                    # print("RowFileAdmin:" + listAdmins)
                    listAdmins = listAdmins.split(";")
                    for row in listAdmins:
                        if not checkIfAdmin(row) and not row == "":
                            row = row.split(";")
                            addAdminToDb(row[0], row[1])
                else:
                    roleLine = row.replace("\n", "")
                    roleLine = roleLine.split("/")
                    print("Roleline: ")
                    print(roleLine)
                    role = roleLine[0]
                    listAdmins = roleLine[1].split(";")
                    print("ListAdmins:: ")
                    print(listAdmins)
                    for admin in listAdmins:
                        if not checkIfAdminHaveRole(admin, role) and not admin == "":
                            countAdded = countAdded + 1
                            print("admin:" + admin)
                            addAdminRole(admin, role)
        except:
            msg = bot.reply_to(message, "Отакої, щось трапилось не так, пришліть текстовий файл ще раз!")
            bot.register_next_step_handler(msg, handle_document_admin, username)
    if countAdded == 0:
        bot.reply_to(message, "Процес завершено, нових адміністраторів не виявлено!")
    elif countAdded > 0:
        bot.reply_to(message, "Адміністратори успішно затягнуті!")


def proccesDocumentAnegdot(message, username):
    countAdded = 0
    with open("listAnegdotsProcces.txt", 'r', encoding="utf8") as fileAnegdot:
        lines = fileAnegdot.readlines()
        try:
            for row in lines:
                if "Category: " in row:
                    category = row.replace("\n", "")
                    category = category.replace("Category: ", "")
                    # print("RowFileAdmin:" + listAdmins)
                    categoryData = category.split(";")
                    if not checkIfExistsCategory(categoryData[0]):
                        countAdded = countAdded + 1
                        addCategoryUsingTxt(categoryData[0], categoryData[1], categoryData[2])
                elif "Anegdot: " in row:
                    anegdot = row.replace("\n", "")
                    anegdot = anegdot.replace("Anegdot: ", "")
                    anegdotData = anegdot.split(";")
                    if not checkIfExistsAnedgot(anegdotData[0], anegdotData[1]):
                        countAdded = countAdded + 1
                        addAnegdotToDbUsingTxt(anegdotData[0], anegdotData[1], anegdotData[2], anegdotData[3])
        except:
            msg = bot.reply_to(message, "Отакої, щось трапилось не так, пришліть текстовий файл ще раз!")
            bot.register_next_step_handler(msg, handle_document_admin, username)
    if countAdded == 0:
        bot.reply_to(message, "Процес завершено, нових категорій або анекдотів не виявлено!")
    elif countAdded > 0:
        bot.reply_to(message, "Категорії та анекдоти успішно затягнуті!")



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
                        row = row.split(";")
                        info += "UserName: " + row[0] + " | Who Added: " + row[1]
                        info += " | "
                        info += "Role: " + GetRole(row[0]) + "\n\n"
                        print(info)
                    f.write(info)
                bot.send_document(message.from_user.id, open(r'listAdmins.txt', 'rb'), reply_markup=types.ReplyKeyboardRemove())
            elif message.text == "Для бази даних":
                with open('listAdmins.txt', 'w', encoding='utf-8') as f:
                    info = ""
                    info += "List of admins: "
                    for row in GetListAndWhoAddOfAdmins():
                        info += row + ";"
                    info += "\n"
                    for row in GetRoleAdminsAll():
                        info += row[1] + "/" + row[2] + "/" + row[3] + "\n"
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
                print(sys.getsizeof(row))
                markup.add(InlineKeyboardButton(row, callback_data="showane: " + row))
            bot.reply_to(message, "Список категорій", reply_markup=markup)
        else:
            msg = bot.reply_to(message, f'Назва категорії: "{message.text}" є занадто довгою ( максимальна кількість символів: {maxNumOfSymsForCategory} )')
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
    maxNumOfSymsForAnegdot = 510
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


def send_meme():
    if checkIfExistChats():
        deleteNoneAnegdots()
        listId = GetChatsId()
        print(listId)
        for row in listId:
            try:
                bot.send_photo(chat_id=row, photo=open('video_2022-09-16_00-28-37.MP4', 'rb'))
                bot.send_message(row, 'Інфа наступна')
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
