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




model.Base.metadata.create_all(bind=engine)


app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='sherly',cursor_factory=RealDictCursor)
        cursor= conn.cursor()
        print("database connected sucessfully")
        break
    except Exception as error:
        print("connection to  the database failed")
        print("Error :",error)
        time.sleep(2)
        

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

@app.get("/posts",response_model=List[schemas.Post])
def get_posts(db :Session =Depends( get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(model.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostCreate   ,db :Session =Depends( get_db)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()  # Commit the transaction to save changes
    new_post=model.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return  new_post




@app.get("/posts/{id}",response_model=schemas.Post)
def get_post(id:int,response:Response,db :Session =Depends( get_db)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """,str(id))
    # post =cursor.fetchone()
    post =db.query(model.Post).filter(model.Post.id == id).first()
    if  post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return {"message":f"post with id {id} was not found "}

    return post



@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT,)
def delete_post(id:int,db :Session =Depends( get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id =%s RETURNING *""",str(id))
    # post = cursor.fetchone()
    # conn.commit()
    post =db.query(model.Post).filter(model.Post.id == id)
    if  post.first is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} donot exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}",response_model=schemas.Post)
def  update_post(id:int,post:schemas.PostCreate,db :Session =Depends( get_db)):
    # cursor.execute("""UPDATE  posts SET title = %s,content=%s,published =%s WHERE id = %s RETURNING *""",(post.title,post.content,post.published ,str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post_q =db.query(model.Post).filter(model.Post.id == id)
    post_up = post_q.first()
    if post_q.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} donot exist")
    post_q.update(post.dict(),synchronize_session =False)
    db.commit()
    return post_q.first()



@app.post("/users", status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate,db:Session=Depends(get_db)):

    #hash the password  -user.password
    hashed_password=utils.hash(user.password)
    user.password=hashed_password

    new_user=model.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/users/{id}",response_model=schemas.UserOut)
def get_user(id:int,db:Session=Depends(get_db)):
    user=db.query(model.User).filter(model.User.id==id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id {id} does not exist")
    return user


