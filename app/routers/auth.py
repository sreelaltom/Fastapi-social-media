from fastapi import APIRouter,HTTPException,Depends,status,Response,status
from sqlalchemy.orm import Session
from .. import database,schemas,model,utils,oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


router = APIRouter(tags=['Authenticatioin'])

@router.post('/login',response_model=schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(database.get_db),):

    #username = 
    #password =
    user =db.query(model.User).filter(model.User.email == user_credentials.username).first()  
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"invalid credentials")
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"invalid credentials")
    
    access_token = oauth2.create_access_token( data= {"user_id":user.id} )
    return{"access_token":access_token,"token_type":"bearer"}

