from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_password_hash, verify_password, create_access_token, 
get_current_user
from .models import User, URL
from .database import SessionLocal

class CreateUserRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UpdateURLLimitRequest(BaseModel):
    username: str
    new_limit: int

class URLRequest(BaseModel):
    url: str
    custom_alias: str = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(request.password)
    new_user = User(username=request.username, hashed_password=hashed_password, url_limit=20)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"User '{new_user.username}' created successfully."}

def list_urls(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin users can view all URLs")
    return db.query(URL).all()

def list_my_urls(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(URL).filter(URL.user_id == current_user.id).all()

def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"message": "Password changed successfully."}

def create_url(request: URLRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_url_count = db.query(URL).filter(URL.user_id == current_user.id).count()
    if user_url_count >= current_user.url_limit:
        raise HTTPException(status_code=400, detail="URL creation limit reached")
    short_url = generate_short_url(request.url, request.custom_alias)
    new_url = URL(short_url=short_url, original_url=request.url, user_id=current_user.id)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return {"short_url": new_url.short_url}

def update_url_limit(request: UpdateURLLimitRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin users can updat URL limits")
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    current_url_count = db.query(URL).filter(URL.user_id == user.id).count()
    if request.new_limit < current_url_count:
        raise HTTPException(status_code=400, detail="New limit is lower than the user's current number of URLs")
    user.url_limit = request.new_limit
    db.commit()
    return {"message": f"Limit updated successfully for '{user.username}'."}

