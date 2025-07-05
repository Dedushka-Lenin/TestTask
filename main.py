import uvicorn

from typing import Literal, List, Union
# from api.applications import FastAPI
from fastapi import FastAPI
from starlette.responses import JSONResponse
from pydantic import BaseModel, constr


####################################################################################################


class People(BaseModel):
    id: constr(min_length=16, max_length=16)
    name: str
    age: int
    gender: Literal['m', 'w']
    nationality: str
    emails: List[str]
    frend:  Union[List[constr(min_length=16, max_length=16)], None] = None


app = FastAPI()


@app.post("/people/{people_id}")
async def create_people(people: People, people_id: int):
    return JSONResponse({"people": people.dict(), "people_id": people_id})

@app.get("/")
async def homepage():
    return JSONResponse({'hello': 'world!!!'})

@app.get("/get_people/{people_id}")
async def read_people(people_id: int):
    print("people_id", people_id)
    return {"people_id": people_id}


####################################################################################################


if __name__ == "__main__":
    uvicorn.run("main:app")