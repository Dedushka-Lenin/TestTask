import uvicorn
import json

from typing import Literal, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, EmailStr, constr, Field



#  Создать возможность связывать людей в дружеские отношения. Дать возможность вывести всех друзей пользователя.
#  Сделать БД



####################################################################################################

try:
    with open('data.json', 'r') as f:
        data = json.load(f)

except:
    data = {}

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


app = FastAPI()

def save_to_json(file_path: str, data_dict: dict):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)

@app.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate):
    if user_id not in data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Обновляем только переданные поля
    update_data = user_update.dict(exclude_unset=True)
    data[user_id].update(update_data)

    save_to_json('data.json', data)
    
    return data[user_id]

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
            "surname" : people.surname,
            "name" : people.name,
            "patronymic" : people.patronymic,
            "age" : people.age,
            "gender" : people.gender,
            "nationality" : people.nationality,
            "emails" : people.emails,
            "friends" : []
        }

    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return {'success':True, 'massege': 'Пользователь успешно добавлен'}


@app.get(                                                                   # endpoint, который принимает Фамилию и выводит информацию о пользователе
    "/get_people{name}",
    tags=['Control and Viewing'],
    summary='Найти пользователя по фамилии'
)
async def get_people(surname: str):

    message = []

    for id in data:
        if surname == data[id]["surname"]:
            message.append(data[id])
            
    return JSONResponse(message)


@app.get(                                                                   # endpoint, который выводит список всех ФИО.
    "/read_people",
    tags=['Control and Viewing'],
    summary='Вывести список всех имен пользователей'
)
async def read_people():

    message = ''
        
    for id in data:
        message += f'{data[id]["surname"]} {data[id]["name"]} {data[id]["patronymic"]}\n'

    return PlainTextResponse(message)


####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")