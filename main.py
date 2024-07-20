from fastapi import FastAPI, HTTPException
from models import URLRequest
from shorten_url import (
 generate_short_url, get_original_url, 
list_all_urls,
)
from exceptions import URLAlreadyExistsException, URLNotFoundException 


app = FastAPI()

class URLRequest(BaseModel):
    url: str
    custom_alias: str = None

@app.post("/shorten_url")
def shorten_url(request: URLRequest):
    try:
        short_url = generate_short_url(request.url, request.custom_alias)
        return {"short_url": short_url}
    except URLAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server 
Error")

@app.get("/list_urls")
def list_urls():
    try:
        urls = list_all_urls()
        return urls
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/{short_url}")
def redirect_url(short_url: str):
    try:
        original_url = get_original_url(short_url)
        return {"original_url": original_url}
    except URLNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal 
Server Error")

    



