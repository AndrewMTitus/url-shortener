from fastapi import FastAPI, Depends, HTTPException, status
from auth import create_access_token, JWTBearer, get_current_user, authenticate_user
from url_management import UpdateURLLimitRequest, CreateUserRequest, ChangePasswordRequest, create_user, list_urls, list_my_urls, change_password, create_url, update_url_limit
from models import User, UserCreate, Token, URLRequest
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import uvicorn

app = FastAPI()

@app.post("/create_user")
def create_user_endpoint(request: CreateUserRequest):
    return create_user(request)

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
def change_user_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user)):
    return change_password(current_user, request.new_password)

@app.post("/create_url", dependencies=[Depends(JWTBearer())])
def create_new_url(request: URLRequest, current_user: User = Depends(get_current_user)):
    return create_url(current_user, request)

# Define the request body model for update_url_limit
class UpdateURLLimitRequest(BaseModel):
    username: str
    new_limit: int

@app.post("/update_url_limit", dependencies=[Depends(JWTBearer())])
def update_user_url_limit(request: UpdateURLLimitRequest):
    return update_url_limit(request.username, request.new_limit)

@app.get("/")
def read_root():
    return {"message": "Welcome to my URL Shortener API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
