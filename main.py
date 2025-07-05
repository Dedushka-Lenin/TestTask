import uvicorn
import json

from typing import Literal, List, Optional
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, constr



#  Разделить name на ФИО
#  Сделать endpoint, который будет принимать фамилию человека и выводить по нему всю сводную информацию.
#  Сделать endpoint, который изменяет информацию о пользователе.
#  Сделать БД
#  Создать возможность связывать людей в дружеские отношения. Дать возможность вывести всех друзей пользователя.
#  endpoint, который выводит список всех пользователей --- список ФИО




####################################################################################################

with open('data.json', 'r') as f:
    data = json.load(f)

# print(data)

class People(BaseModel):
    id: constr(pattern=r'^\d{16}$')
    name: str
    age: int
    gender: Literal['m', 'w']
    nationality: str
    emails: List[EmailStr]
    friends:  Optional[List[constr(pattern=r'^\d{16}$')]] = None


app = FastAPI()



@app.post(                                                                   # endpoint, который принимает информацию о новом человеке и создает запись в БД.  (Пока не в БД)
    "/create_people",
    tags=['Control and Viewing'],
    summary='Создать пользователя'
)
async def create_people(people: People):

    id = len(data)+1

    while f"{id:016d}" in data:
        shift += 1
        id += 1


    data[f"{id:016d}"] = {
            "name": people.name,
            "age": people.age,
            "gender": people.gender,
            "nationality": people.nationality,
            "emails": people.emails,
        }

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return {'success':True, 'massege': 'Пользователь успешно добавлен'}


@app.get(                                                                   # endpoint, который выводит список всех пользователей.
    "/get_people{id}",
    tags=['Control and Viewing'],
    summary='Найти пользователя по id'
)
async def get_people(id: str):
    return data[id]


@app.get(                                                                   # endpoint, принимает id и выводит информацию о пользователе
    "/read_people",
    tags=['Control and Viewing'],
    summary='Вывести список всех пользователей'
)
async def read_people():
    return data


####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")