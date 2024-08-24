from fastapi import FastAPI, HTTPException, Depends, status
from auth import create_access_token, JWTBearer, get_current_user, get_current_active_user
from models import User, UserCreate
from url_management import (
    create_url, list_my_urls, list_all_urls, update_url_limit
)
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn

app = FastAPI()

class URLRequest(BaseModel):
    url: str
    custom_alias: str = None

@app.post("/create_user")
def create_user(user: UserCreate):
    return create_user_in_db(user)

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/list_urls", dependencies=[Depends(JWTBearer())])
def list_all_urls_for_admin():
    return list_urls()

@app.get("/list_my_urls", dependencies=[Depends(JWTBearer())])
def list_urls_for_user(current_user: User = Depends(get_current_user)):
    return list_my_urls(current_user)

@app.post("/change_password", dependencies=[Depends(JWTBearer())])
def change_user_password(current_user: User = Depends(get_current_user), new_password: str):
    return change_password(current_user, new_password)

@app.post("/create_url", dependencies=[Depends(JWTBearer())])
def create_new_url(current_user: User = Depends(get_current_user), url_request: URLRequest):
    return create_url(current_user, url_request)

@app.post("/update_url_limit", dependencies=[Depends(JWTBearer())])
def update_user_url_limit(username: str, new_limit: int):
    return update_url_limit(username, new_limit)

@app.get("/")
def read_root():
    return {"message": "Welcome to my URL Shortener API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




