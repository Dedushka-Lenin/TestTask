import sqlite3
import json



class ControlDB():
    def __init__(self):
        # Устанавливаем соединение с базой данных
        self.connection = sqlite3.connect('db/people.db')
        self.cursor = self.connection.cursor()

        # Создаем таблицу Tasks
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS People (
                id INTEGER PRIMARY KEY, -- id
                surname TEXT NOT NULL, -- Фамилия
                name TEXT NOT NULL, -- Имя
                patronymic TEXT NOT NULL, -- Отчество
                age INTEGER NOT NULL CHECK (age > 0) CHECK (age < 151), -- Возраст
                gender TEXT NOT NULL CHECK (gender IN ('w', 'm')), -- Пол
                nationality TEXT NOT NULL, -- Национальность
                emails TEXT NOT NULL, -- Электронные адреса
                friends TEXT DEFAULT '[]' -- Список друзей в виде JSON массива
            );
        ''')

    def close_db(self):
       self.connection.close()


    # Функция проверки наличия
    def check_availability(self, id):
        self.cursor.execute("SELECT 1 FROM People WHERE id = ?", (id,))
        exists = self.cursor.fetchone() is not None

        if exists:
            return {'exists':exists, 'massege': 'Пользователя с таким id существует'}

        return {'exists':exists, 'massege': 'Пользователя с таким id не существует'}


    # Функция для вывода фамилий пользоватей
    def read_peopleBD(self):

        message = ''

        self.cursor.execute('SELECT surname, name, patronymic FROM People')
        people = self.cursor.fetchall()

        for human in people:
            surname, name, patronymic = human
            message += f"{surname} {name} {patronymic}\n"

        return message
    

    # Функция для вывода информации по фамилии пользователя
    def get_peopleBD(self, surname):
        # Выполняем запрос с параметром для защиты от SQL-инъекций
        self.cursor.execute('SELECT * FROM People WHERE surname = ?', (surname,))
        users = self.cursor.fetchall()
        
        if not users:
            return {'success':False, 'massege': 'Пользователя с таким id не существует'}
        
        # Получаем названия столбцов
        columns = [desc[0] for desc in self.cursor.description]
        
        # Создаем список словарей для всех найденных пользователей
        result = []
        for user in users:
            user_dict = {columns[i]: user[i] for i in range(len(columns))}
            result.append(user_dict)
        
        return result
    

    # Функция для добавления нового пользователя
    def create_peoplBD(self, surname, name, patronymic, age, gender, nationality, emails, friends='[]'):

        emails = json.dumps(emails)

        self.cursor.execute('''
            INSERT INTO People (surname, name, patronymic, age, gender, nationality, emails, friends)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (surname, name, patronymic, age, gender, nationality, emails, friends))

        self.connection.commit()


    # Функция для удаления пользователя
    def delete_peopleDB(self, id):

        success = self.check_availability(id)
        if not success['exists']:
            return success['massege']

        self.cursor.execute(f"SELECT friends FROM People WHERE id = ?", (id,))
        list_friend = self.cursor.fetchone()
        list_friend = json.loads(list_friend[0]) if list_friend and list_friend[0] is not None else []

        for friend in list_friend:
            self.control_friendsDB(id, friend, 'end')

        self.cursor.execute(f"DELETE FROM People WHERE id = ?", (id,))
        self.connection.commit()

        return {'success':True, 'massege': 'Пользователь успешно удален'}


    # Функция для изменения пользователя
    def update_peopleDB(self, id, column_name, new_value):

        success = self.check_availability(id)
        if not success['exists']:
            return success['massege']

        if column_name is not None:

            self.cursor.execute(f"UPDATE People SET {column_name} = ? WHERE id = ?", (new_value, id))
            self.connection.commit()

        return {'success':True, 'massege': 'Изменения успешно внесяны'}


    def control_friendsDB(self, friend_1, friend_2, start_end_being_friends):

        success = self.check_availability(id)
        if not success['exists']:
            return success['massege']

        self.cursor.execute(f"SELECT friends FROM People WHERE id = ?", (friend_1,))
        list_friend_1 = self.cursor.fetchone()
        list_friend_1 = json.loads(list_friend_1[0]) if list_friend_1 and list_friend_1[0] is not None else []

        self.cursor.execute(f"SELECT friends FROM People WHERE id = ?", (friend_2,))
        list_friend_2 = self.cursor.fetchone()
        list_friend_2 = json.loads(list_friend_2[0]) if list_friend_2 and list_friend_2[0] is not None else []

        match start_end_being_friends:
            case 'start':

                if friend_2 in list_friend_1:
                    return {'success':False, 'massege': 'Пользователи уже являются друзьями'}

                list_friend_1.append(friend_2)
                list_friend_2.append(friend_1)

                massege = 'Пользователи успешно подружились'

            case 'end':

                if not friend_2 in list_friend_1:
                    return {'success':False, 'massege': 'Пользователи не являются друзьями'}

                list_friend_1.remove(friend_2)
                list_friend_2.remove(friend_1)

                massege = 'Пользователи успешно перестали дружить'

        self.update_peopleDB(friend_1, 'friends', json.dumps(list_friend_1))
        self.update_peopleDB(friend_2, 'friends', json.dumps(list_friend_2))

        return {'success':True, 'massege': massege}
    
        
    def list_friendsDB(self, id):

        success = self.check_availability(id)
        if not success['exists']:
            return success['massege']
        
        self.cursor.execute(f"SELECT friends FROM People WHERE id = ?", (id,))
        list_friend = self.cursor.fetchone()
        list_friend = json.loads(list_friend[0]) if list_friend and list_friend[0] is not None else []

        return list_friend