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


app = FastAPI()

controlDB = ControlDB()

def signal_handler(sig, frame):
    controlDB.close_db()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


####################################################################################################



class People(BaseModel):
    # id: constr(pattern=r'^\d{16}$')
    surname: str = Field(max_length=20)
    name: str = Field(max_length=20)
    patronymic: str = Field(max_length=20)
    age: int = Field(ge=0, le=150)
    gender: Literal['m', 'w']
    nationality: str = Field(max_length=20)
    emails: List[EmailStr]

# Модель для обновления (может быть частичным)
class UserUpdate(BaseModel):
    surname: Optional[str]
    name: Optional[str]
    patronymic: Optional[str]
    age: Optional[int]
    gender: Optional[Literal['m', 'w']]
    nationality: Optional[str]
    emails: Optional[List[EmailStr]]


def save_to_json(file_path: str, data_dict: dict):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)



@app.put("/users/{user_id}"                                                 # endpoint, который изменяет информацию о пользователе.
         )                                                
async def update_user(user_id: str, user_update: UserUpdate):

    
    return {'success':True, 'massege': 'Пользователь успешно изменён'}


@app.post(                                                                   # endpoint, который принимает информацию о новом человеке и создает запись в БД.  (Пока не в БД)
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