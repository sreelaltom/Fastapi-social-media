from fastapi import FastAPI
from . import model
from .database import engine
from .routers import post,user,auth

model.Base.metadata.create_all(bind=engine)

app = FastAPI()
        

@app.get("/")
async def root():
    return {"message":"hello"}

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)