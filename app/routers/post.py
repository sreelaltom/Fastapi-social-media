from .. import model ,schemas,utils,oauth2
from fastapi import Body, FastAPI,Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from .. database import get_db
from typing import List,Optional

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/",response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db),limit: int = 10,skip: int = 0,search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    print(search)
    print(limit)
    posts = db.query(model.Post).filter(model.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostCreate   ,db :Session =Depends( get_db),current_user :int =Depends(oauth2.get_current_user)):
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()  # Commit the transaction to save changes
    print(current_user.email)
    new_post=model.Post(owner_id =current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return  new_post




@router.get("/{id}",response_model=schemas.Post)
def get_post(id:int,response:Response,db :Session =Depends( get_db)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """,str(id))
    # post =cursor.fetchone()
    post =db.query(model.Post).filter(model.Post.id == id).first()
    if  post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} was not found")
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return {"message":f"post with id {id} was not found "}

    return post



@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT,)
def delete_post(id:int,db :Session =Depends( get_db),current_user:int =Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id =%s RETURNING *""",str(id))
    # post = cursor.fetchone()
    # conn.commit()
    post =db.query(model.Post).filter(model.Post.id == id)
    if  post.first is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} donot exist")
    
    if post.owner_id  != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="not authorized to perform requested action")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}",response_model=schemas.Post)
def  update_post(id:int,post:schemas.PostCreate,db :Session =Depends( get_db),current_user :int =Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE  posts SET title = %s,content=%s,published =%s WHERE id = %s RETURNING *""",(post.title,post.content,post.published ,str(id)))
    # post = cursor.fetchone()
    # conn.commit()
    post_q =db.query(model.Post).filter(model.Post.id == id)
    post_up = post_q.first()
    if post_q.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id {id} donot exist")
    if post_up.owner_id  != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="not authorized to perform requested action")
    post_q.update(post.dict(),synchronize_session =False)
    db.commit()
    return post_q.first()

