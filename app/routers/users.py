from fastapi import HTTPException, status, APIRouter

from app.database import SessionDep
from app.models import Users, UserCreate, UserResponse
from app.utils import get_hash

router = APIRouter(prefix="/users", tags=['Users'])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, session: SessionDep) -> Users:
    new_user = Users(email=user.email, password=get_hash(user.password))
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.get('/{_id}', response_model=UserResponse)
def get_user(_id: int, session: SessionDep) -> type[Users]:
    user = session.get(Users, _id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user/{_id} not found')
    return user
