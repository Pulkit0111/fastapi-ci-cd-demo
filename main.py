from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import SessionLocal, UserDB

app = FastAPI()


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic model for user creation
class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    age: Optional[int] = Field(
        None,
        gt=0,
        lt=100,
        description="The age of the user should be greater than 0 and less than 100",
    )
    email: EmailStr


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI with uv!"}


@app.get("/greet/{name}")
def greet_user(name: str, age: Optional[int] = None):
    if age:
        return {"message": f"Hello, {name}! You are {age} years old."}
    else:
        return {"message": f"Hello, {name}!"}


@app.post("/create-user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )

    # Create new user
    new_user = UserDB(name=user.name, age=user.age, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"User {new_user.name} created!",
        "user": new_user,
    }


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(UserDB).all()
    return {"users": users}
