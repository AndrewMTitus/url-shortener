from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from auth import create_access_token, JWTBearer, get_current_user, get_current_active_user
from models import User, URL
from database import SessionLocal
from url_management import (
    create_url, list_my_urls, list_all_urls, update_url_limit
)
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class URLRequest(BaseModel):
    url: str
    custom_alias: str = None

@app.post("/create_user")
def create_user(username: str, password: str, db: Session = Depends(SessionLocal)):
    hashed_password = get_password_hash(password)
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": f"User '{username}' created successfully."}

@app.post("/shorten_url", dependencies=[Depends(get_current_active_user)])
def shorten_url(request: URLRequest, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    try:
        short_url = create_url(db, request.url, request.custom_alias, current_user)
        return {"short_url": short_url.short_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/list_my_urls", dependencies=[Depends(get_current_active_user)])
def list_my_urls(db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    try:
        urls = list_my_urls(db, current_user)
        return urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_urls", dependencies=[Depends(get_current_active_user)])
def list_urls(db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    try:
        urls = list_all_urls(db, current_user)
        return urls
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/change_password", dependencies=[Depends(get_current_active_user)])
def change_password(old_password: str, new_password: str, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect.")
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Password changed successfully."}

@app.post("/update_url_limit", dependencies=[Depends(get_current_active_user)])
def update_url_limit(username: str, new_limit: int, db: Session = Depends(SessionLocal), current_user: User = Depends(get_current_user)):
    try:
        updated_user = update_url_limit(db, username, new_limit, current_user)
        return {"message": f"Limit updated successfully for '{username}'."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/")
def read_root():
    return {"message": "Welcome to my URL Shortener API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




