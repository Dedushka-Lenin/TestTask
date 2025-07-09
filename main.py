import uvicorn
import json
import signal
import sys

from typing import Literal, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, EmailStr, constr, Field

from db.control_db import ControlDB


#  Создать возможность связывать людей в дружеские отношения. Дать возможность вывести всех друзей пользователя.


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
    age: int = Field(default=0, ge=0, le=150)
    gender: Literal['m', 'w'] = ''
    nationality: str = Field(default='', max_length=20)
    emails: List[EmailStr] = Field(default_factory=list)

# Модель для обновления (может быть частичным)
class PeopleUpdate(BaseModel):
    surname: Optional[str] = Field(default_factory=None)
    name: Optional[str] = Field(default_factory=None)
    patronymic: Optional[str] = Field(default_factory=None)
    age: Optional[int] = Field(default_factory=None)
    gender: Optional[Literal['m', 'w']] = Field(default_factory=None)
    nationality: Optional[str] = Field(default_factory=None)
    emails: Optional[List[EmailStr]] = Field(default_factory=None)


####################################################################################################
# блок для работы с друзьями

@app.put("/control_friends/{friend_1}/{friend_2}/{start_or_end}",                       # endpoint, который упровляет друзьями
    tags=['Manage Friends'],
    summary='Контроль друзей')                                                
async def control_friends(friend_1: str, friend_2: str, start_or_end: Literal['end', 'start']):



    pass


@app.put("/control_friends/{id}",                                                       # endpoint, который выводит список друзей
    tags=['Manage Friends'],
    summary='Список друзей')                                                
async def list_friends(id: str):

    massege = []

    massege.append(controlDB.get_DB(table_name='Friends', field_name='friend_1', value=id))
    massege.append(controlDB.get_DB(table_name='Friends', field_name='friend_2', value=id))

    return massege


####################################################################################################
# блок для работы с пользователями

@app.put("/delete_people/{user_id}",                                                    # endpoint, который удаляет пользователя
    tags=['Adding and Сhanging'],
    summary='Удаление пользователя')                                                
async def delete_people(id: str):

    massege = controlDB.delete_DB(table_name='People', field_name='id', value=id)
    massege = controlDB.delete_DB(table_name='Friends', field_name='friend_1', value=id)
    massege = controlDB.delete_DB(table_name='Friends', field_name='friend_2', value=id)
    massege = controlDB.delete_DB(table_name='Emails', field_name='id_people', value=id)

    return massege


@app.put("/сhange_people/{user_id}",                                                    # endpoint, который изменяет информацию о пользователе
    tags=['Adding and Сhanging'],
    summary='Изменение пользователя')                                                
async def update_people(id: str, update_people: PeopleUpdate):

    # Проверка существования записи
    success = controlDB.check_availability_record(table_name='People', field_name='id', value=id)
    if not success['exists']:
        return success['massege']

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
    
    return {'success':True, 'massege': 'Пользователь успешно инзменен'}


@app.post(                                                                              # endpoint, который принимает информацию о новом человеке и создает запись в БД
    "/create_people",
    tags=['Adding and Сhanging'],
    summary='Создать пользователя'
)
async def create_people(people: People):

    controlDB.insert_into_table(
                table_name='People', 
                data_dict=people
            )

    return {'success':True, 'massege': 'Пользователь успешно добавлен'}


####################################################################################################
# болок для вывода информации о пользователях

@app.get(                                                                               # endpoint, который принимает Фамилию и выводит информацию о пользователе
    "/get_people{surname}",
    tags=['Info'],
    summary='Найти пользователя по фамилии'
)
async def get_people(surname: str):

    message = controlDB.get_DB(table_name='People', field_name='surname', value=surname)
            
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

    return PlainTextResponse(message)


####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")