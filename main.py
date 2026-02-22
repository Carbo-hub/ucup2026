from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, lang: str = "ua"):
    if lang not in ["ua", "en"]:
        lang = "ua"
        
    file_path = f"static/locales/{lang}.json"
    with open(file_path, "r", encoding="utf-8") as file:
        site_data = json.load(file)

    css_path = "static/style.css"
    css_version = int(os.path.getmtime(css_path)) if os.path.exists(css_path) else 1

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "current_lang": lang,
            "css_version": css_version,
            "ucup_logo": "/static/logos/ucup.png",
            "ui": site_data["ui"],
            "events": site_data["events"],
            "schedule": site_data["schedule"],
            "organizers": site_data["organizers"],
            "participants": site_data["participants"],
            "sponsors": site_data["sponsors"],
            "main_organizer": site_data["main_organizer"]
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)