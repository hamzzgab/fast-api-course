from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import select

from app.database import SessionDep
from app.models import Users, Token
from app.oauth2 import create_access_token
from app.utils import verify

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=Token)
def login(user_credential: OAuth2PasswordRequestForm = Depends(), session: SessionDep = None):
    user = session.exec(select(Users).where(Users.email == user_credential.username)).first()
    if not user or not verify(user_credential.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid Credentials')

    access_token = create_access_token(data={'user_id': user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
