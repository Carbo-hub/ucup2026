from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import json
import os
import requests
import csv
from io import StringIO

# Configuration for Google Sheets
SHEET_ID = "1Lkk4nV5__U08CltEl5UVwqWYEpWzdtPx1qZ_Y_ohs9w" 
GID_TEAMS = "125322421"  # Tab: Teams (with absolute ranks)
GID_MEDALS = "497974982" # Tab: Medals (points rules)
GID_NEWS = "792434601"   # Tab: News

# In-memory cache for instant page loading
CACHE = {
    "teams": [],
    "medals": [],
    "news": []
}

def fetch_sheet_data(gid="0"):
    """Fetch data from Google Sheets instantly as CSV."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        response.encoding = 'utf-8' # Fix for Cyrillic characters
        reader = csv.DictReader(StringIO(response.text))
        return list(reader)
    except Exception as e:
        print(f"[ERROR] Failed to fetch data from Google Sheets (GID: {gid}). Details: {e}")
        return []

async def update_cache_loop():
    """Background task to update cache every 30 seconds without blocking the server."""
    while True:
        try:
            # asyncio.to_thread prevents requests.get from blocking the main FastAPI event loop
            CACHE["teams"] = await asyncio.to_thread(fetch_sheet_data, GID_TEAMS)
            CACHE["medals"] = await asyncio.to_thread(fetch_sheet_data, GID_MEDALS)
            CACHE["news"] = await asyncio.to_thread(fetch_sheet_data, GID_NEWS)
        except Exception as e:
            print(f"[ERROR] Background cache update failed: {e}")
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager to handle startup and shutdown events."""
    print("[INFO] Initializing cache from Google Sheets...")
    CACHE["teams"] = fetch_sheet_data(gid=GID_TEAMS)
    CACHE["medals"] = fetch_sheet_data(gid=GID_MEDALS)
    CACHE["news"] = fetch_sheet_data(gid=GID_NEWS)
    
    # Start the background update loop
    task = asyncio.create_task(update_cache_loop())
    yield
    # Cancel the loop on shutdown
    task.cancel()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_base_context(request: Request, lang: str):
    """Retrieve common data required for every page (Header, Footer, Partners)."""
    if lang not in ["ua", "en"]:
        lang = "ua"
        
    with open(f"static/locales/{lang}.json", "r", encoding="utf-8") as file:
        site_data = json.load(file)

    css_path = "static/style.css"
    css_version = int(os.path.getmtime(css_path)) if os.path.exists(css_path) else 1

    return {
        "request": request,
        "current_lang": lang,
        "css_version": css_version,
        "ucup_logo": "/static/logos/ucup.png",
        "ui": site_data["ui"],
        "participants": site_data["participants"],
        "sponsors": site_data["sponsors"],
        "main_organizer": site_data["main_organizer"]
    }

# --- PAGE ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def page_info(request: Request, lang: str = "ua"):
    ctx = get_base_context(request, lang)
    with open(f"static/locales/{ctx['current_lang']}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        ctx["main_events"] = data.get("main_events", [])
        ctx["side_events"] = data.get("side_events", [])
    return templates.TemplateResponse(request=request, name="index.html", context=ctx)

@app.get("/news", response_class=HTMLResponse)
async def page_news(request: Request, lang: str = "ua"):
    ctx = get_base_context(request, lang)
    # Using instant data from cache instead of fetching on load
    ctx["news"] = CACHE["news"]
    return templates.TemplateResponse(request=request, name="news.html", context=ctx)

@app.get("/schedule", response_class=HTMLResponse)
async def page_schedule(request: Request, lang: str = "ua"):
    ctx = get_base_context(request, lang)
    with open(f"static/locales/{ctx['current_lang']}.json", "r", encoding="utf-8") as f:
        ctx["schedule"] = json.load(f).get("schedule", [])
    return templates.TemplateResponse(request=request, name="schedule.html", context=ctx)

@app.get("/standings", response_class=HTMLResponse)
async def page_standings(request: Request, lang: str = "ua"):
    ctx = get_base_context(request, lang)
    return templates.TemplateResponse(request=request, name="standings.html", context=ctx)

# --- API FOR LIVE UPDATES ---

@app.get("/api/standings")
async def api_standings():
    """Returns teams and medal rules instantly from cache."""
    return JSONResponse(content={"teams": CACHE["teams"], "medals": CACHE["medals"]})

if __name__ == "__main__":
    print("[INFO] Starting FastAPI server on 127.0.0.1:8080...")
    uvicorn.run(app, host="127.0.0.1", port=8080)