from prometheus_client import Counter, generate_latest
from fastapi import FastAPI, Depends, HTTPException, status, Response
from auth import create_access_token, JWTBearer, get_current_user, authenticate_user
from url_management import UpdateURLLimitRequest, CreateUserRequest, ChangePasswordRequest, create_user, list_urls, list_my_urls, change_password, create_url, update_url_limit
from models import User, UserCreate, Token, URLRequest
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from config import settings, get_dynamodb_table
import uvicorn

app = FastAPI()

# Initialize Prometheus Instrumentation
Instrumentator().instrument(app).expose(app)

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
def list_all_urls_for_admin(current_user: User = Depends(get_current_user)):
    #Check if the current user is an admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You don't have permission to access this resource")
    
    #if the current user is an admin, they can access the list of all URLs
    return list_urls()

@app.get("/list_my_urls", dependencies=[Depends(JWTBearer())])
def list_urls_for_user(current_user: User = Depends(get_current_user)):
    return list_my_urls(current_user)

@app.get("/lookup/{short_url}")
def lookup_url(short_url: str):
    # Query your database or URL storage to find the original URL
    urls_table = get_dynamodb_table(settings.URLS_TABLE_NAME)
    url_data = urls_table.get_item(Key={"short_url": short_url}).get("Item")
    if url_data:
        return {"original_url": url_data["original_url"]}
    else:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
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


# Define a Counter to track the number of HTTP requests
REQUEST_COUNT = Counter("request_count", "Total number of HTTP requests")

@app.middleware("http")
async def track_requests(request, call_next):
    # Increment the request count on each HTTP request
    REQUEST_COUNT.inc()
    response = await call_next(request)
    return response

@app.get("/metrics")
async def get_metrics():
    # Generate and return Prometheus metrics
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

