from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models import Vote, Votes, Posts
from app.oauth2 import get_current_user

router = APIRouter(prefix="/vote", tags=['Vote'])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create(vote: Vote, session: SessionDep, current_user: int = Depends(get_current_user)):
    if not session.get(Posts, vote.post_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post does not exist")

    query = session.exec(select(Votes).where(Votes.post_id == vote.post_id, Votes.user_id == current_user))
    found_vote = query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'user_id: {current_user} has already voted')

        new_vote = Votes(post_id=vote.post_id, user_id=current_user)
        session.add(new_vote)
        session.commit()
        return {
            "message": "successfully added vote"
        }
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"vote does not exist")
        session.delete(found_vote)
        session.commit()
        return {
            "message": "deleted vote"
        }

