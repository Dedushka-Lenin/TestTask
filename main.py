import uvicorn

from typing import Literal, List, Optional
# from api.applications import FastAPI
from fastapi import FastAPI
from starlette.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, constr, EmailStr


####################################################################################################


class People(BaseModel):
    id: constr(pattern=r'^\d{8}$')
    name: str
    age: int
    gender: Literal['m', 'w']
    nationality: str
    emails: List[EmailStr]
    friends:  Optional[List[constr(pattern=r'^\d{8}$')]] = None


app = FastAPI()


@app.post("/create people", tags=['Control and Viewing'])
async def create_people(people: People, people_id: int):
    return JSONResponse({"people": people.dict(), "people_id": people_id})

# @app.get("/")
# async def homepage():
#     return 

@app.get("/read people", tags=['Control and Viewing'])
async def read_people(people_id: int):
    print("people_id", people_id)

    return {"people_id": people_id}


####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")