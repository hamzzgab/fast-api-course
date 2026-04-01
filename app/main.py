from fastapi import FastAPI

from app.database import lifespan
from app.routers import posts, users, auth

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "welcome to the api"}

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
