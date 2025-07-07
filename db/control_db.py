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


    # Функция для добавления нового пользователя
    def create_peoplBD(self, surname, name, patronymic, age, gender, nationality, emails, friends='[]'):

        emails = json.dumps(emails)

        self.cursor.execute('''
            INSERT INTO People (surname, name, patronymic, age, gender, nationality, emails, friends)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (surname, name, patronymic, age, gender, nationality, emails, friends))

        self.connection.commit()


    # Функция для вывода информации по фамилии пользователя
    def get_peopleBD(self, surname):
        # Выполняем запрос с параметром для защиты от SQL-инъекций
        self.cursor.execute('SELECT * FROM People WHERE surname = ?', (surname,))
        users = self.cursor.fetchall()
        
        if not users:
            return f"Пользователи с фамилией '{surname}' не найдены."
        
        # Получаем названия столбцов
        columns = [desc[0] for desc in self.cursor.description]
        
        # Создаем список словарей для всех найденных пользователей
        result = []
        for user in users:
            user_dict = {columns[i]: user[i] for i in range(len(columns))}
            result.append(user_dict)
        
        return result


    # Функция для вывода фамилий пользоватей
    def read_peopleBD(self):

        message = ''

        self.cursor.execute('SELECT surname, name, patronymic FROM People')
        people = self.cursor.fetchall()

        for human in people:
            surname, name, patronymic = human
            message += f"{surname} {name} {patronymic}\n"

        return message