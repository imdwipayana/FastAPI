# FastAPI SQLAlchemy
# CRUD Operation / HTTP Requests
# Create - POST
# Read - GET
# Update - PUT
# Delete - DELETE

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

# Security Config
SECRET_KEY = "codewithjosh"
ALGORITHM = "HS256"
TOKEN_EXPIRES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI(title="Integration with SQL")

# Database setup
engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class User(Base):
    __tablename__  = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100), nullable=False)
    hashed_pwd = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(engine)

# Pydantic Models (Dataclass)
class  UserCreate(BaseModel):
    name:str
    email:str
    role:str
    password: str

class UserResponse(BaseModel):
    id:int
    name:str
    email:str
    role:str
    is_active: bool

    class Config:
        from_attributes = True


# New Pydantic Models
class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    email:Optional[str] = None

# Security Functions
def verify_pwd(plain_pwd:str, hashed_pwd:str) -> bool:
    return pwd_context.verify(plain_pwd, hashed_pwd)

def get_pwd_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data:dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire =datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() +timedelta(minutes=15)

    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email:str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail = "Could not verify credentials",
                headers = {"WWW-Authenticate":"Bearer"}
            )
        return TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Could not verify credentials",
            headers = {"WWW-Authenticate":"Bearer"}
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth Dependencies



# Endpoints (www.zerotoknowing.com/)
@app.get("/")
def root():
    return {"message":"Intro to Fast API with SQL"}

@app.get("/users/{user_id}",response_model=UserResponse)
def get_user(user_id:int, db:Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=404, detail="User already exists")
    
    # Create a new user
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Update user
@app.put("/user/{user_id}", response_model=UserResponse)
def update_user(user_id:int, user:UserCreate, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="User doesnot exist!")
    
    for field, value in user.dict().items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# Delete User
@app.delete("/users/{user_id}")
def delete_user(user_id:int, db:Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User does not exist!")
    
    db.delete(db_user)
    db.commit()
    return {"message":"User deleted!"}

# Get all users
@app.get("/users/", response_model=List[UserResponse])
def get_all_users(db:Session = Depends(get_db)):
    return db.query(User).all()


