import sqlite3


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
                gender TEXT NOT NULL CHECK (gender IN ('male', 'female')), -- Пол
                nationality TEXT NOT NULL -- Национальность
            );
        ''')

        # Создаем таблицу Emails
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Emails (
                id INTEGER PRIMARY KEY, -- id
                id_people INTEGER NOT NULL CHECK (id_people > 0), -- id пользователя
                email TEXT NOT NULL CHECK (email LIKE '%@%')-- привязанный имэйл
            );
        ''')

        # Создаем таблицу Friends
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Friends (
                id INTEGER PRIMARY KEY, -- id
                id_friend_1 INTEGER NOT NULL CHECK (id_friend_1 > 0), -- id первого друга
                id_friend_2 INTEGER NOT NULL CHECK (id_friend_2 > 0) -- id второго друга
            );
        ''')

    def close_DB(self):
       self.connection.close()


    # Функция проверки существования таблицы
    def check_table_exists(self, table_name):

        self.cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name=?
        """, (table_name,))

        exists = bool(self.cursor.fetchone())

        if exists:
            return {'exists': exists, 'message': 'Таблица не найдена'}

        return {'exists':exists, 'message': 'Таблица найдена'}


    # Функция проверки наличия записи
    def check_availability_record(self, table_name, field_name, value):

        success = self.check_table_exists(table_name=table_name)
        if not success['exists']:
            return success['message']

        self.cursor.execute(f"SELECT 1 FROM {table_name} WHERE {field_name} = ?", (value,))
        exists = self.cursor.fetchone() is not None

        if not exists:
            return {'exists': exists, 'message': f'Запись {value} не найдена в столбце {field_name}'}

        return {'exists':exists, 'message': 'Запись найдена'}


    # Функция для вывода столбцов
    def read_DB(self, table_name, field_name):
        success = self.check_table_exists(table_name=table_name)
        if not success['exists']:
            return success['message']

        self.cursor.execute(f'SELECT {field_name} FROM {table_name}')
        results = self.cursor.fetchall()

        message = [row[0] for row in results]

        return message
    
    
    # Функция для вывода информации по значению столбца
    def get_DB(self, table_name, field_name, value):

        success = self.check_table_exists(table_name=table_name)
        if not success['exists']:
            return success['message']

        self.cursor.execute(f"SELECT * FROM {table_name} WHERE {field_name} = ?", (value,))
        rows = self.cursor.fetchall()

        if not rows:
            return []

        # Получаем названия столбцов
        columns = [desc[0] for desc in self.cursor.description]

        # Создаем список словарей для всех найденных записей
        result = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]

        return result


    # Функция для добавления нового столбца
    def insert_into_table(self, table_name, data_dict):

        success = self.check_table_exists(table_name=table_name)
        if not success['exists']:
            return success['message']

        columns = ', '.join(data_dict.keys())
        placeholders = ', '.join(['?'] * len(data_dict))
        values = tuple(data_dict.values())

        self.cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
        self.connection.commit()

        inserted_id = self.cursor.lastrowid
        return inserted_id


    # Функция удаления записи
    def delete_DB(self, table_name, field_name, value):
        
        # Проверка существования записи
        success = self.check_availability_record(table_name=table_name, field_name=field_name, value=value)
        if not success['exists']:
            return success['message']
        
        # Удаление записи
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {field_name} = ?", (value,))
        self.connection.commit()
        
        return {'exists': True, 'message': 'Запись успешно удалена'}
    
    
    # Функция для изменения записи
    def update_BD(self, table_name, id, field_name, value):
        # Проверка ограничения (например, для поля age)
        try:
            self.cursor.execute(f"UPDATE {table_name} SET {field_name} = ? WHERE id = ?", (value, id))
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print(f"Ошибка при обновлении: {e}")
            return {'exists': False, 'message': str(e)}
        return {'exists': True, 'message': 'Изменения успешно внесены'}