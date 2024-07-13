from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from shorten_url import (
 generate_short_url, get_original_url, 
list_all_urls,
) 


app = FastAPI()

class URLRequest(BaseModel):
    url: str
    custom_alias: str = None

@app.post("/shorten_url")
def shorten_url(request: URLRequest):
    try:
        short_url = generate_short_url(request.url, request.custom_alias)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

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
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    



