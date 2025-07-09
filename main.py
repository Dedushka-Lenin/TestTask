import uvicorn
import signal
import sys
import requests

from typing import Literal, List, Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

from db.control_db import ControlDB


####################################################################################################


controlDB = ControlDB()

def signal_handler(sig, frame):
    controlDB.close_DB()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


####################################################################################################


app = FastAPI()

# Модель для добавления
class People(BaseModel):
    surname: str = Field(default='', max_length=20)
    name: str = Field(default='', max_length=20)
    patronymic: str = Field(default='', max_length=20)
    emails: List[EmailStr] = Field(default_factory=list)

# Модель для обновления (может быть частичным)
class PeopleUpdate(BaseModel):
    surname: Optional[str] = Field(default_factory=None)
    name: Optional[str] = Field(default_factory=None)
    patronymic: Optional[str] = Field(default_factory=None)
    age: Optional[int] = Field(default_factory=None)
    gender: Optional[Literal['male', 'female']] = Field(default_factory=None)
    nationality: Optional[str] = Field(default_factory=None)
    emails: Optional[List[EmailStr]] = Field(default_factory=None)


####################################################################################################


def get_age(name):
    response = requests.get(f"https://api.agify.io?name={name}")
    if response.status_code == 200:
        data = response.json()
        return data.get('age')
    return None

def get_gender(name):
    response = requests.get(f"https://api.genderize.io?name={name}")
    if response.status_code == 200:
        data = response.json()
        return data.get('gender')
    return None

def get_nationality(name):
    response = requests.get(f"https://api.nationalize.io?name={name}")
    if response.status_code == 200:
        data = response.json()
        country_data = data.get('country', [])
        if country_data:
            country_data.sort(key=lambda x: x['probability'], reverse=True)
            return country_data[0]['country_id']
    return None


####################################################################################################
# блок для работы с друзьями

@app.put("/control_friends/{friend_1}/{friend_2}/{start_or_end}",                       # endpoint, который упровляет друзьями
    tags=['Manage Friends'],
    summary='Контроль друзей')                                                
async def control_friends(friend_1: int, friend_2: int, start_or_end: Literal['end', 'start']):

    success = controlDB.check_availability_record(table_name='People', field_name='id', value=friend_1)
    if not success['exists']:
        return success['message']
    
    success = controlDB.check_availability_record(table_name='People', field_name='id', value=friend_2)
    if not success['exists']:
        return success['message']


    f1 = controlDB.get_DB(table_name='Friends', field_name='id_friend_1', value=friend_1)

    f2 = controlDB.get_DB(table_name='Friends', field_name='id_friend_2', value=friend_1)

    for d in f2: 
        d['id_friend_1'], d['id_friend_2'] = d['id_friend_2'], d['id_friend_1']

    list_friend_1 = f1 + f2


    match start_or_end:
        case 'start':

            exists = any(d.get('id_friend_2') == friend_2 for d in list_friend_1)

            if exists:
                return {'success':True, 'message': 'Пользователи уже являются друзьями'}

            else:
                controlDB.insert_into_table(
                    table_name='Friends', 
                    data_dict={
                        'id_friend_1' : friend_1,
                        'id_friend_2' : friend_2
                    }
                )

                return {'success':True, 'message': 'Пользователи успешно подружились'}

        case 'end':

            matching_dict = next(
                (d for d in list_friend_1 if d.get('id_friend_2') == friend_2),
                None
            )

            if matching_dict:
                
                controlDB.delete_DB(table_name='Friends', field_name='id', value=matching_dict['id'])
                
                return {'success':True, 'message': 'Пользователи успешно перестали подружить'}

            else:
            
                return {'success':True, 'message': 'Пользователи не являются друзьями'}


@app.get("/control_friends/{id}",                                                       # endpoint, который выводит список друзей
    tags=['Manage Friends'],
    summary='Список друзей')                                                
async def list_friends(id: int):

    success = controlDB.check_availability_record(table_name='People', field_name='id', value=id)
    if not success['exists']:
        return success['message']

    f1 = controlDB.get_DB(table_name='Friends', field_name='id_friend_1', value=id)

    f2 = controlDB.get_DB(table_name='Friends', field_name='id_friend_2', value=id)

    for d in f2: 
        d['id_friend_1'], d['id_friend_2'] = d['id_friend_2'], d['id_friend_1']

    list_friend = f1 + f2

    list_friend = [d['id_friend_2'] for d in list_friend]

    message = []

    for f_id in list_friend:

        frend = controlDB.get_DB(table_name='People', field_name='id', value=f_id)[0]

        del frend['id']
        del frend['age']
        del frend['gender']
        del frend['nationality']

        message.append(frend)

    return message

####################################################################################################
# блок для работы с пользователями

@app.delete("/delete_people/{user_id}",                                                    # endpoint, который удаляет пользователя
    tags=['Adding and Сhanging'],
    summary='Удаление пользователя')                                                
async def delete_people(id: int):

    message = controlDB.delete_DB(table_name='People', field_name='id', value=id)
    message = controlDB.delete_DB(table_name='Friends', field_name='id_friend_1', value=id)
    message = controlDB.delete_DB(table_name='Friends', field_name='id_friend_2', value=id)
    message = controlDB.delete_DB(table_name='Emails', field_name='id_people', value=id)

    return message


@app.put("/сhange_people/{user_id}",                                                    # endpoint, который изменяет информацию о пользователе
    tags=['Adding and Сhanging'],
    summary='Изменение пользователя')                                                
async def update_people(id: str, update_people: PeopleUpdate):

    # Проверка существования записи
    success = controlDB.check_availability_record(table_name='People', field_name='id', value=id)
    if not success['exists']:
        return success['message']

    if update_people.emails is not None:

        controlDB.delete_DB(table_name='Emails', field_name='id_people', value=id)

        for elm in update_people.emails:
            controlDB.insert_into_table(
                table_name='Emails', 
                data_dict={
                    'id_people' : id,
                    'email' : elm
                }
            )

    controlDB.update_BD(table_name='People', id=id, field_name='surname', value=update_people.surname)
    controlDB.update_BD(table_name='People', id=id, field_name='name', value=update_people.name)
    controlDB.update_BD(table_name='People', id=id, field_name='patronymic', value=update_people.patronymic)
    controlDB.update_BD(table_name='People', id=id, field_name='age', value=update_people.age)
    controlDB.update_BD(table_name='People', id=id, field_name='gender', value=update_people.gender)
    controlDB.update_BD(table_name='People', id=id, field_name='nationality', value=update_people.nationality)
    
    return {'success':True, 'message': 'Пользователь успешно инзменен'}


@app.post(                                                                              # endpoint, который принимает информацию о новом человеке и создает запись в БД
    "/create_people",
    tags=['Adding and Сhanging'],
    summary='Создать пользователя'
)
async def create_people(people: People):

    data_dict = {
        'surname' : people.surname,
        'name' : people.name,
        'patronymic' : people.patronymic,
        'age' : get_age(people.name),
        'gender' : get_gender(people.name),
        'nationality' : get_nationality(people.name)
    }

    id = controlDB.insert_into_table(
                table_name='People', 
                data_dict=data_dict
            )
    
    for elm in people.emails:
        controlDB.insert_into_table(
                table_name='Emails', 
                data_dict={
                    'id_people' : id,
                    'email' : elm
                }
            )

    return {'success':True, 'message': 'Пользователь успешно добавлен'}


####################################################################################################
# болок для вывода информации о пользователях

@app.get(                                                                               # endpoint, который принимает Фамилию и выводит информацию о пользователе
    "/get_people{surname}",
    tags=['Info'],
    summary='Найти пользователя по фамилии'
)
async def get_people(surname: str):

    message = controlDB.get_DB(table_name='People', field_name='surname', value=surname)

    for elm in message:

        emails = controlDB.get_DB(table_name='Emails', field_name='id_people', value=elm['id'])

        email_list = []

        for email in emails:

            email_list.append(email['email'])

        elm['email'] = email_list
            
    return JSONResponse(message)


@app.get(                                                                               # endpoint, который выводит список всех ФИО.
    "/read_people",
    tags=['Info'],
    summary='Вывести список всех имен пользователей'
)
async def read_people():

    id_list = controlDB.read_DB(table_name='People', field_name='id')
    surname_list = controlDB.read_DB(table_name='People', field_name='surname')
    name_list = controlDB.read_DB(table_name='People', field_name='name')
    patronymic_list = controlDB.read_DB(table_name='People', field_name='patronymic')

    keys = ['id', 'surname', 'name', 'patronymic']

    message = [dict(zip(keys, values)) for values in zip(id_list, surname_list, name_list, patronymic_list)]

    return message


####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")