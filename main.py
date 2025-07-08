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
    controlDB.close_db()
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
    surname: Optional[str]
    name: Optional[str]
    patronymic: Optional[str]
    age: Optional[int]
    gender: Optional[Literal['m', 'w']]
    nationality: Optional[str]
    emails: Optional[List[EmailStr]]


####################################################################################################
# блок для работы с друзьями

@app.put("/control_friends/{friend_1}/{friend_2}/{start_or_end}",                     # endpoint, который упровляет друзьями
    tags=['Manage Friends'],
    summary='Контроль друзей')                                                
async def control_friends(friend_1: str, friend_2: str, start_or_end: Literal['end', 'start']):

    massege = controlDB.control_friendsDB(friend_1, friend_2, start_or_end)
    
    return massege


@app.put("/control_friends/{id}",                     # endpoint, который выводит список друзей
    tags=['Manage Friends'],
    summary='Список друзей')                                                
async def list_friends(id: str):

    massege = controlDB.list_friendsDB(id)
    
    return massege


####################################################################################################
# блок для работы с пользователями

@app.put("/delete_people/{user_id}",                                                 # endpoint, который удаляет пользователя
    tags=['Adding and Сhanging'],
    summary='Удаление пользователя')                                                
async def delete_people(id: str):

    massege = controlDB.delete_peopleDB(id)

    return massege


@app.put("/сhange_people/{user_id}",                                                 # endpoint, который изменяет информацию о пользователе
    tags=['Adding and Сhanging'],
    summary='Изменение пользователя')                                                
async def update_people(id: str, update_people: PeopleUpdate):

    massege = controlDB.check_availability(id)
    if not massege['exists']:
        return massege['massege']

    controlDB.update_peopleDB(id, 'surname', update_people.surname)
    controlDB.update_peopleDB(id, 'name', update_people.name)
    controlDB.update_peopleDB(id, 'patronymic', update_people.patronymic)
    controlDB.update_peopleDB(id, 'age', update_people.age)
    controlDB.update_peopleDB(id, 'gender', update_people.gender)
    controlDB.update_peopleDB(id, 'nationality', update_people.nationality)
    controlDB.update_peopleDB(id, 'emails', json.dumps(update_people.emails))
    
    return {'success':True, 'massege': 'Пользователь успешно инзменен'}


@app.post(                                                                   # endpoint, который принимает информацию о новом человеке и создает запись в БД
    "/create_people",
    tags=['Adding and Сhanging'],
    summary='Создать пользователя'
)
async def create_people(people: People):

    controlDB.create_peoplBD(
        surname = people.surname,
        name = people.name,
        patronymic = people.patronymic,
        age = people.age,
        gender = people.gender,
        nationality = people.nationality,
        emails = people.emails
    )

    return {'success':True, 'massege': 'Пользователь успешно добавлен'}


####################################################################################################
# болок для вывода информации о пользователях

@app.get(                                                                   # endpoint, который принимает Фамилию и выводит информацию о пользователе
    "/get_people{surname}",
    tags=['Info'],
    summary='Найти пользователя по фамилии'
)
async def get_people(surname: str):
    message = controlDB.get_peopleBD(surname)
            
    return JSONResponse(message)


@app.get(                                                                   # endpoint, который выводит список всех ФИО.
    "/read_people",
    tags=['Info'],
    summary='Вывести список всех имен пользователей'
)
async def read_people():
    message = controlDB.read_peopleBD()

    return PlainTextResponse(message)


####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")