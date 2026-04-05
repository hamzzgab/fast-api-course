from fastapi import HTTPException, Response, status, APIRouter
from fastapi.params import Depends
from sqlalchemy import func
from sqlmodel import select, col

from app.database import SessionDep
from app.models import Posts, PostUpdate, PostResponse, Votes, PostsWithVotes
from app.oauth2 import get_current_user

router = APIRouter(prefix='/posts', tags=['Posts'])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_posts(post: Posts,
                 session: SessionDep,
                 current_user: int = Depends(get_current_user)) -> Posts:
    post.user_id = current_user
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.get("/", response_model=list[PostsWithVotes])
def get_posts(session: SessionDep,
              current_user: int = Depends(get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: str = ""
              ):
    count_votes = func.count(Votes.post_id).label("num_votes")
    statement = (
        select(Posts, count_votes)
        .where(col(Posts.title).contains(search))
        .join(Votes, isouter=True)
        .group_by(Posts.id)
        .order_by(count_votes.desc())
        .offset(skip)
        .limit(limit)
    )
    results = session.exec(statement).all()
    return [{"post": post, "num_votes": num_votes} for post, num_votes in results]


@router.get("/{_id}", response_model=PostResponse)
def get_post(_id: int, session: SessionDep, current_user: int = Depends(get_current_user)) -> type[Posts]:
    post = session.get(Posts, _id)
    num_votes = len(session.exec(select(Votes).where(Votes.post_id == _id)).all())
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'posts/{_id} not found')
    return post


@router.put("/{_id}", response_model=PostResponse)
def update_post(_id: int,
                post_update: PostUpdate,
                session: SessionDep,
                current_user: int = Depends(get_current_user)) -> type[Posts]:
    post = session.get(Posts, _id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'posts/{_id} not found')

    if post.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorised for action')

    post.title = post_update.title
    post.content = post_update.content
    post.is_published = post_update.is_published

    session.add(post)
    session.commit()
    session.refresh(post)

    return post


@router.delete("/{_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(_id: int,
                session: SessionDep,
                current_user: int = Depends(get_current_user)):
    post = session.get(Posts, _id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'posts/{_id} not found')

    if post.user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorised for action')

    session.delete(post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
