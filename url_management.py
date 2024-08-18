from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from models import URL, User
from auth import get_current_user, get_current_active_user
from database import SessionLocal

def create_url(db: Session, original_url: str, custom_alias: str, current_user: User):
    if current_user.url_count >= current_user.url_limit:
        raise HTTPException(status_code=400, detail="URL creation limit reached.")
    url = URL(original_url=original_url, short_url=custom_alias, owner_id=current_user.id)
    db.add(url)
    db.commit()
    db.refresh(url)
    current_user.url_count += 1
    db.commit()
    return url

def list_my_urls(db: Session, current_user: User):
    return db.query(URL).filter(URL.owner_id == current_user.id).all()

def list_all_urls(db: Session, current_user: User):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view all URLs.")
    return db.query(URL).all()

def update_url_limit(db: Session, username: str, new_limit: int, current_user: User):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update limits.")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if new_limit < user.url_count:
        raise HTTPException(status_code=400, detail="New limit cannot be less than the current URL count.")
    user.url_limit = new_limit
    db.commit()
    return user
