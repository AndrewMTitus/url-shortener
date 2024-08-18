from fastapi import FastAPI, Depends
from auth import JWTBearer
from url_management import (
    create_user,
    list_urls,
    list_my_urls,
    change_password,
    create_url,
    update_url_limit,
    CreateUserRequest,
    ChangePasswordRequest,
    URLRequest,
    UpdateURLLimitRequest,
)
import uvicorn

app = FastAPI()

@app.post("/create_user", dependencies=[Depends(JWTBearer())])
def create_user_endpoint(request: CreateUserRequest):
    return create_user(request)

@app.get("/list_urls", dependencies=[Depends(JWTBearer())])
def list_urls_endpoint():
    return list_urls()

@app.get("/list_my_urls", dependencies=[Depends(JWTBearer())])
def list_my_urls_endpoint():
    return list_my_urls()

@app.post("/change_password", dependencies=[Depends(JWTBearer())])
def change_password_endpoint(request: ChangePasswordRequest):
    return change_password(request)

@app.post("/create_url", dependencies=[Depends(JWTBearer())])
def create_url_endpoint(request: URLRequest):
    return create_url(request)

@app.post("/update_url_limit", dependencies=[Depends(JWTBearer())])
def update_url_limit_endpoint(request: UpdateURLLimitRequest):
    return update_url_limit(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
