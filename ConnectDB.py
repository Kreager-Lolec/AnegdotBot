import random
import datetime
from datetime import *
import psycopg2
import Constant_File

mydb = psycopg2.connect(Constant_File.DB_URI)
roleName = ['Юнлінг', 'Падаван', 'Лицар-джедай', 'гранд-майстер Ордена джедаїв']


def CreateTable():
    mycursor = mydb.cursor()
    mycursor.execute('''
        CREATE TABLE IF NOT EXISTS CHATS (
            ChatId BIGINT PRIMARY KEY,
            CountUsers BIGINT ); ''')
    mydb.commit()
    mycursor.execute(''' 
        CREATE TABLE IF NOT EXISTS CATEGORIES (
            CaterogyId INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
            CategoryNameDisplay VARCHAR(255) NOT NULL,
            CategoryNameLogical VARCHAR(255) NOT NULL,
            UserNameAdded VARCHAR(255) NOT NULL,
            TimeAdded VARCHAR(255) NOT NULL
        );
                   ''')
    mydb.commit()
    mycursor.execute('''
            CREATE TABLE IF NOT EXISTS ANEGDOTS (
                AnegdotId INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
                AnegdotDisplay VARCHAR(510) NOT NULL,
                AnegdotLogical VARCHAR(510) NOT NULL,
                CategoryNameDisplay VARCHAR(255) NOT NULL,
                CategoryNameLogical VARCHAR(255) NOT NULL,
                UserNameAdded VARCHAR(255) NOT NULL,
                TimeAdded VARCHAR(255) NOT NULL
        );
                       ''')
    mydb.commit()
    mycursor.execute('''
            CREATE TABLE IF NOT EXISTS TEMPANEGDOT (
                AnegdotId INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
                AnegdotDisplay VARCHAR(510) NOT NULL,
                AnegdotLogical VARCHAR(510) NOT NULL,
                CategoryNameDisplay VARCHAR(255) NOT NULL,
                CategoryNameLogical VARCHAR(255) NOT NULL,
                UserNameAdded VARCHAR(255) NOT NULL,
                TimeAdded VARCHAR(255) NOT NULL
        );
                       ''')
    mydb.commit()
    mycursor.execute('''
            CREATE TABLE IF NOT EXISTS ROLES_ADMIN (
                RoleId INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
                RoleName VARCHAR(255) NOT NULL,
                ListAdmins VARCHAR(255) NOT NULL,
                ListRights VARCHAR(255) NOT NULL
        );
                       ''')
    mydb.commit()
    mycursor.execute('''
            CREATE TABLE IF NOT EXISTS ADMINS (
                AdminId INTEGER NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
                AdminUserName VARCHAR(255) NOT NULL,
                AdminWhoAdd VARCHAR(255) NOT NULL
        );
                       ''')
    mydb.commit()
    listadmin = ['mihailik_panchuk', 'zhuranskyi', 'Barik_superman']
    listwhoadd = ['Auto Added By System', 'Auto Added By System', 'Auto Added By System']
    # listAdminId = ['156911032','256266717','399228453']
    i = 0
    while i < len(listadmin):
        mycursor.execute(f'''INSERT INTO ADMINS (AdminUserName, AdminWhoAdd)
        SELECT N'{listadmin[i]}', N'{listwhoadd[i]}'
        WHERE
            NOT EXISTS (SELECT * FROM ADMINS WHERE AdminUserName = N'{listadmin[i]}' ) ''')
        i = i + 1
    mydb.commit()
    insertRoles()
    mycursor.close()


def insertRoles():
    listadmin = ['mihailik_panchuk', 'zhuranskyi', 'Barik_superman']
    listRights = ['addcategory', 'addanegdot', 'deletecategory', 'deleteanegdot', 'gettxtanegdot', 'gettxtadmins',
                  'controladmin', 'inserttxtcategoriesandanegdotstodb', 'inserttxtadminstodb']
    listUnlingRights = listRights[0] + ";" + listRights[1]
    listPadavanRights = listUnlingRights + ";" + listRights[2] + ";" + listRights[3]
    listJediKnightRights = listPadavanRights + ";" + listRights[4] + ";" + listRights[5]
    listGrandMasterRights = listJediKnightRights + ";" + listRights[6] + ";" + listRights[7] + ";" + listRights[8]
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO ROLES_ADMIN (roleName, listAdmins, Listrights)
    SELECT N'{roleName[0]}', '', N'{listUnlingRights}'
    WHERE
        NOT EXISTS (SELECT * FROM ROLES_ADMIN WHERE roleName = N'{roleName[0]}' ) ''')
    mydb.commit()
    mycursor.execute(f'''INSERT INTO ROLES_ADMIN (roleName, listAdmins, Listrights)
    SELECT N'{roleName[1]}', '', N'{listPadavanRights}'
    WHERE
        NOT EXISTS (SELECT * FROM ROLES_ADMIN WHERE roleName = N'{roleName[1]}' ) ''')
    mydb.commit()
    mycursor.execute(f'''INSERT INTO ROLES_ADMIN (roleName, listAdmins, Listrights)
    SELECT N'{roleName[2]}', '', N'{listJediKnightRights}'
    WHERE
        NOT EXISTS (SELECT * FROM ROLES_ADMIN WHERE roleName = N'{roleName[2]}' ) ''')
    mydb.commit()
    mycursor.execute(f'''INSERT INTO ROLES_ADMIN (roleName, listAdmins, Listrights)
    SELECT N'{roleName[3]}', '', N'{listGrandMasterRights}'
    WHERE
        NOT EXISTS (SELECT * FROM ROLES_ADMIN WHERE roleName = N'{roleName[3]}' ) ''')
    mydb.commit()
    if not checkIfHaveAnyRole(listadmin[2]):
        print("Don't have role: " + listadmin[2])
        removeAdminRoleWhileSetNew(listadmin[2])
        addAdminRole(listadmin[2], roleName[1])
    if not checkIfHaveAnyRole(listadmin[0]):
        print("Don't have role: " + listadmin[0])
        removeAdminRoleWhileSetNew(listadmin[0])
        addAdminRole(listadmin[0], roleName[2])
    if not checkIfHaveAnyRole(listadmin[1]):
        print("Don't have role: " + listadmin[1])
        removeAdminRoleWhileSetNew(listadmin[1])
        addAdminRole(listadmin[1], roleName[3])
    mycursor.close()


def checkIfHaveAnyRole(username):
    haveRole = False
    for row in roleName:
        if checkIfAdminHaveRole(username, row):
            print("Have role")
            haveRole = True
    return haveRole


def addAdminToDb(userName, userNameWhoAdd):
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO ADMINS (AdminUserName, AdminWhoAdd)
    SELECT N'{userName}', N'{userNameWhoAdd}'
    WHERE
        NOT EXISTS (SELECT * FROM ADMINS WHERE AdminUserName = N'{userName}' AND  AdminWhoAdd = N'{userNameWhoAdd}') ''')
    mydb.commit()
    mycursor.close()


def getCountOfAdmins():
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT COUNT(*) FROM ADMINS ''')
    return mycursor.fetchone()[0]


def deleteAdmin(userName):
    mycursor = mydb.cursor()
    mycursor.execute(f'''DELETE FROM ADMINS WHERE AdminUserName = N'{userName}' ''')
    mydb.commit()
    mycursor.close()


def addAdminRole(adminUserName,role):
    mycursor = mydb.cursor()
    expression = getAdminListByRole(role) + adminUserName + "||"
    mycursor.execute(f'''UPDATE ROLES_ADMIN
    SET listAdmins = N'{expression}'
    WHERE roleName = N'{role}' ''')
    mydb.commit()
    mycursor.close()


def removeAdminRoleWhileSetNew(adminUserName):
    mycursor = mydb.cursor()
    roleName = ['Юнлінг', 'Падаван', 'Лицар-джедай', 'гранд-майстер Ордена джедаїв']
    for row in roleName:
        listAdminds = getAdminListByRole(row)
        listAdminds = listAdminds.replace(adminUserName + "||", "")
        mycursor.execute(f'''UPDATE ROLES_ADMIN
        SET listAdmins = N'{listAdminds}'
        WHERE roleName = N'{row}' ''')
        mydb.commit()
    mycursor.close()


def removeAdminRole(adminUserName,role):
    mycursor = mydb.cursor()
    listAdminds = getAdminListByRole(role)
    listAdminds = listAdminds.replace(adminUserName + "||", "")
    mycursor.execute(f'''UPDATE ROLES_ADMIN
    SET listAdmins = N'{listAdminds}'
    WHERE roleName = N'{role}' ''')
    mydb.commit()
    mycursor.close()


# def getAdminIdByName(username):
#     mycursor = mydb.cursor()
#     mycursor.execute(f'''SELECT listAdmins FROM ADMINS WHERE AdminUserName = N'{username}' ''')
#     info = mycursor.fetchone()[0]
#     print("Admin: " + info)
#     return info


def getAdminListByRole(role):
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT listAdmins FROM ROLES_ADMIN WHERE roleName = N'{role}' ''')
    info = mycursor.fetchone()[0]
    print("Admin: " + info)
    return info


def checkIfAdminHaveRole(adminUserName,role):
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT listAdmins FROM ROLES_ADMIN WHERE roleName = N'{role}' ''')
    listAdminds = mycursor.fetchone()[0]
    mycursor.execute(f'''SELECT RoleName FROM ROLES_ADMIN WHERE roleName = N'{role}' ''')
    RoleName = mycursor.fetchone()[0]
    print("Admin: " + listAdminds + " Role: " + RoleName)
    adminsdata = str(listAdminds).split("||")
    for row in adminsdata:
        if adminUserName == row:
            return True
    return False


def GetRole(adminUserName):
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM ROLES_ADMIN ''')
    info = mycursor.fetchall()
    print("Info in GetRole: " + str(info))
    for row in info:
        listAdmins = str(row[2]).split("||")
        role = str(row[1])
        for srow in listAdmins:
            if adminUserName == srow:
                print("GetRoleInfo: " + role)
                return role
    return "Ніхуя"


def GetListAndWhoAddOfAdmins():
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM ADMINS ''')
    info = mycursor.fetchall()
    listAdmins = []
    for row in info:
        listAdmins.append(row[1] + "~" + row[2])
    print(listAdmins)
    return listAdmins


def GetAdminRights(adminUserName):
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM ROLES_ADMIN ''')
    info = mycursor.fetchall()
    for row in info:
        if checkIfAdminHaveRole(adminUserName,row[1]):
            # print(row[3])
            return row[3]


def GetRoleAdminsAll():
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM ROLES_ADMIN ''')
    info = mycursor.fetchall()
    return info


def checkIfAdmin(username):
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT COUNT(*) FROM ADMINS WHERE AdminUserName = N'{username}' ''')
    if mycursor.fetchone()[0] == 1:
        return True
    return False


def checkIfExistChats():
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT COUNT(*) FROM CHATS''')
    if mycursor.fetchone()[0] > 0:
        return True
    return False


def GetChatsId():
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM CHATS''')
    listId = []
    for row in mycursor.fetchall():
        listId.append(row[0])
        print(row[0])
    return listId


def checkIfExistsCategory(categoryLogical):
    category = proccesAnegdotOrCategoryName(categoryLogical)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT COUNT(*) FROM CATEGORIES WHERE CategoryNameLogical = %s ", (category,))
    if mycursor.fetchone()[0] == 1:
        return True
    return False


def checkIfExistsAnedgot(anegdotLogical, categoryLogical):
    anegdot = proccesAnegdotOrCategoryName(anegdotLogical)
    category = proccesAnegdotOrCategoryName(categoryLogical)
    mycursor = mydb.cursor()
    mycursor.execute(
        f'''SELECT COUNT(*) FROM ANEGDOTS WHERE AnegdotLogical = %s AND CategoryNameLogical = %s''', (anegdot, category,))
    if mycursor.fetchone()[0] == 1:
        print("Anegdot exist: " + anegdotLogical)
        return True
    return False


def checkIfExistsAnedgotWithoutCategory(anegdotLogical):
    anegdot = proccesAnegdotOrCategoryName(anegdotLogical)
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT COUNT(*) FROM ANEGDOTS WHERE AnegdotLogical = %s''', (anegdot,))
    if mycursor.fetchone()[0] == 1:
        return True
    return False


def checkIfNotExistAnedgots():
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT COUNT(*) FROM ANEGDOTS''')
    if mycursor.fetchone()[0] == 0:
        return True
    return False


def checkIfNotExistCategories():
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT COUNT(*) FROM CATEGORIES''')
    if mycursor.fetchone()[0] == 0:
        return True
    return False


def checkIfNotExistAnedgotsByCategory(categoryLogical):
    category = proccesAnegdotOrCategoryName(categoryLogical)
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT COUNT(*) FROM ANEGDOTS WHERE CategoryNameLogical = %s''', (category,))
    if mycursor.fetchone()[0] == 0:
        return True
    return False


def addCategory(message):
    categoryNameDisplay = str(message.text).strip(" ")
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryNameDisplay)
    userName = message.from_user.username
    time = datetime.now()
    time = str(time.strftime("%H:%M:%S %d-%m-%y"))
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO CATEGORIES (CategoryNameDisplay, CategoryNameLogical, UserNameAdded, TimeAdded)
    SELECT %s, %s, %s, %s
    WHERE
        NOT EXISTS (SELECT * FROM CATEGORIES WHERE CategoryNameLogical = %s) ''', (categoryNameDisplay, categoryNameLogical, userName, time, categoryNameLogical,))
    mydb.commit()
    mycursor.close()


def addCategoryApprove(category, username):
    categoryNameDisplay = category.strip(" ")
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryNameDisplay)
    userName = username
    time = datetime.now()
    time = str(time.strftime("%H:%M:%S %d-%m-%y"))
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO CATEGORIES (CategoryNameDisplay, CategoryNameLogical, UserNameAdded, TimeAdded)
    SELECT %s, %s, %s, %s
    WHERE
        NOT EXISTS (SELECT * FROM CATEGORIES WHERE CategoryNameLogical = %s) ''', (categoryNameDisplay, categoryNameLogical, userName, time, categoryNameLogical,))
    mydb.commit()
    mycursor.close()


def addCategoryUsingTxt(category,userName,time):
    categoryNameDisplay = str(category).strip(" ")
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryNameDisplay)
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO CATEGORIES (CategoryNameDisplay, CategoryNameLogical, UserNameAdded, TimeAdded)
    SELECT %s, %s, %s, %s
    WHERE
        NOT EXISTS (SELECT * FROM CATEGORIES WHERE CategoryNameLogical = %s) ''', (categoryNameDisplay, categoryNameLogical, userName, time, categoryNameLogical,))
    mydb.commit()
    mycursor.close()


def addAnegdotToDb(message, category):
    categoryNameDisplay = category.strip(" ")
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryNameDisplay)
    anegdotDisplay = str(message.text).strip(" ")
    anegdotLogical = proccesAnegdotOrCategoryName(anegdotDisplay)
    userName = message.from_user.username
    time = datetime.now()
    time = str(time.strftime("%H:%M:%S %d-%m-%y"))
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO ANEGDOTS (AnegdotDisplay,AnegdotLogical,CategoryNameDisplay,CategoryNameLogical,UserNameAdded,TimeAdded)
    SELECT %s, %s, %s, %s, %s, %s
    WHERE
        NOT EXISTS (SELECT * FROM ANEGDOTS WHERE CategoryNameLogical = %s AND AnegdotLogical = %s)'''
                     , (anegdotDisplay, anegdotLogical, categoryNameDisplay, categoryNameLogical, userName, time, categoryNameLogical, anegdotLogical,))
    mydb.commit()
    mycursor.close()


def addAnegdotToDbApprove(anegdot, category, username):
    categoryNameDisplay = category.strip(" ")
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryNameDisplay)
    anegdotDisplay = anegdot.strip(" ")
    anegdotLogical = proccesAnegdotOrCategoryName(anegdotDisplay)
    userName = username
    time = datetime.now()
    time = str(time.strftime("%H:%M:%S %d-%m-%y"))
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO ANEGDOTS (AnegdotDisplay,AnegdotLogical,CategoryNameDisplay,CategoryNameLogical,UserNameAdded,TimeAdded)
    SELECT %s, %s, %s, %s, %s, %s
    WHERE
        NOT EXISTS (SELECT * FROM ANEGDOTS WHERE CategoryNameLogical = %s AND AnegdotLogical = %s)'''
                     , (anegdotDisplay, anegdotLogical, categoryNameDisplay, categoryNameLogical, userName, time, categoryNameLogical, anegdotLogical,))
    mydb.commit()
    mycursor.close()


def addAnegdotToDbUsingTxt(anegdot, category, userName, time):
    categoryNameDisplay = category.strip(" ")
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryNameDisplay)
    anegdotDisplay = anegdot.strip(" ")
    anegdotLogical = proccesAnegdotOrCategoryName(anegdotDisplay)
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO ANEGDOTS (AnegdotDisplay,AnegdotLogical,CategoryNameDisplay,CategoryNameLogical,UserNameAdded,TimeAdded)
    SELECT %s, %s, %s, %s, %s, %s
    WHERE
        NOT EXISTS (SELECT * FROM ANEGDOTS WHERE CategoryNameLogical = %s AND AnegdotLogical = %s)''',
                     (anegdotDisplay, anegdotLogical, categoryNameDisplay, categoryNameLogical, userName, time, categoryNameLogical, anegdotLogical,))
    mydb.commit()
    mycursor.close()


def removeAnegdotFromDb(anegdot):
    anegdotLogical = proccesAnegdotOrCategoryName(str(anegdot))
    mycursor = mydb.cursor()
    mycursor.execute(f''' DELETE FROM ANEGDOTS WHERE AnegdotLogical = %s''', (anegdotLogical,))
    mydb.commit()
    mycursor.close()

def deleteCategoryWithAllJokes(category):
    categoryNameLogical = proccesAnegdotOrCategoryName(category)
    mycursor = mydb.cursor()

    # Спочатку видаляємо анекдоти
    mycursor.execute("DELETE FROM ANEGDOTS WHERE CategoryNameLogical = %s", (categoryNameLogical,))
    mydb.commit()

    # Потім видаляємо саму категорію
    mycursor.execute("DELETE FROM CATEGORIES WHERE CategoryNameLogical = %s", (categoryNameLogical,))
    mydb.commit()

    mycursor.close()
    print(f"Категорію '{category}' та всі її анекдоти успішно видалено.")



def AddChat(message):
    mycursor = mydb.cursor()
    mycursor.execute(f'''INSERT INTO CHATS (ChatId)
    SELECT {message.chat.id}
    WHERE
        NOT EXISTS (SELECT * FROM CHATS WHERE ChatId = {message.chat.id} ) ''')
    mydb.commit()
    mycursor.close()


def getCategories():
    mycursor = mydb.cursor()
    mycursor.execute('''SELECT * FROM CATEGORIES''')
    info = mycursor.fetchall()
    listCategories = []
    for row in info:
        listCategories.append(row[1])
    print(listCategories)
    return listCategories


def getFullInfoCategories():
    mycursor = mydb.cursor()
    mycursor.execute('''SELECT * FROM CATEGORIES''')
    info = mycursor.fetchall()
    return info


def getAnegdot():
    mycursor = mydb.cursor()
    mycursor.execute('''SELECT * FROM ANEGDOTS''')
    info = mycursor.fetchall()
    listAnegdots = []
    for row in info:
        listAnegdots.append(row[1])
    print(listAnegdots)
    anegdot = random.choice(listAnegdots)
    return anegdot


def getRandomAnegdotByCategory(categoryname):
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryname)
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM ANEGDOTS WHERE CategoryNameLogical = %s''', (categoryNameLogical,))
    info = mycursor.fetchall()
    listAnegdots = []
    for row in info:
        listAnegdots.append(row[1])
    print(listAnegdots)
    anegdot = random.choice(listAnegdots)
    return anegdot


def getAnegdotsByCategory(categoryname):
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryname)
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM ANEGDOTS WHERE CategoryNameLogical = %s ''', (categoryNameLogical,))
    info = mycursor.fetchall()
    listAnegdots = []
    for row in info:
        listAnegdots.append(row[1])
    print(listAnegdots)
    return listAnegdots


def getFullInfoAnegdotsByCategory(categoryname):
    categoryNameLogical = proccesAnegdotOrCategoryName(categoryname)
    mycursor = mydb.cursor()
    mycursor.execute(f'''SELECT * FROM ANEGDOTS WHERE CategoryNameLogical = %s ''', (categoryNameLogical,))
    info = mycursor.fetchall()
    return info


def deleteCategory(category):
    categoryNameLogical = proccesAnegdotOrCategoryName(category)
    mycursor = mydb.cursor()
    mycursor.execute(f"DELETE FROM CATEGORIES WHERE CategoryNameLogical = %s ", (categoryNameLogical,))
    mydb.commit()
    mycursor.close()


def deleteAnegdotsByCategory(category):
    categoryNameLogical = proccesAnegdotOrCategoryName(category)
    print(category)
    mycursor = mydb.cursor()
    mycursor.execute(f"DELETE FROM ANEGDOTS WHERE CategoryNameLogical = %s ", (categoryNameLogical,))
    mydb.commit()
    mycursor.close()


def deleteNoneAnegdots():
    mycursor = mydb.cursor()
    mycursor.execute(f"DELETE FROM ANEGDOTS WHERE AnegdotDisplay = 'None' ")
    mydb.commit()
    mycursor.close()


def DeleteChat(chat_id):
    mycursor = mydb.cursor()
    mycursor.execute(f"DELETE FROM CHATS WHERE ChatId = '{chat_id}' ")
    mydb.commit()
    mycursor.close()


def deleteExactlyAnegdots():
    mycursor = mydb.cursor()
    mycursor.execute(f"DELETE FROM ANEGDOTS WHERE AnegdotDisplay = '       ' ")
    mydb.commit()
    mycursor.close()


def deleteExactlyAdmin():
    mycursor = mydb.cursor()
    mycursor.execute(f"DELETE FROM ADMINS WHERE AdminUserName = '       ' ")
    mydb.commit()
    mycursor.close()


def deleteExactlyCategories():
    mycursor = mydb.cursor()
    mycursor.execute(f"DELETE FROM CATEGORIES WHERE CategoryNameDisplay = 'ААААААААААААААААААААААААААААААААААААААААААААААААААААААА' ")
    mydb.commit()
    mycursor.close()


def proccesAnegdotOrCategoryName(name):
    completeName = str(name).strip(" ")
    completeName = completeName.lower()
    return completeName


def DropTable():
    mycursor = mydb.cursor()
    # mycursor.execute('''DROP TABLE ANEGDOTS''')
    # mycursor.execute('''DROP TABLE CATEGORIES''')
    mycursor.execute('''DROP TABLE ADMINS''')
    mycursor.execute('''DROP TABLE ROLES_ADMIN''')
    mydb.commit()
    mycursor.close()


def ShowChats():
    mycursor = mydb.cursor()
    mycursor.execute('''SELECT * FROM CHATS''')
    for row in mycursor:
        print(row)
    mydb.commit()
    mycursor.close()