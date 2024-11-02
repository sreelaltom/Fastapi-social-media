from typing import Optional,List
from fastapi import Body, FastAPI,Response,status,HTTPException,Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import model,schemas,utils
from .database import engine,get_db
from sqlalchemy.orm import Session
from .routers import post,user,auth




model.Base.metadata.create_all(bind=engine)


app = FastAPI()



        

my_posts = [{"title":"title of the post 1","content":"content of post 1","published":False,"id":1},
            {"title":"new college","content":"i joined a new college","id":2}]

def find_post(id):
    for i in my_posts:
        if i["id"]==id:
            return i
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id :
            return i

@app.get("/")
async def root():
    return {"message":"man"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)