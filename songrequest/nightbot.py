import json
import os
from datetime import datetime, timezone
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import requests
from starlette.templating import Jinja2Templates

from songrequest.settings import ApplicationSettings

load_dotenv()

token_path = Path("token.json")
port = 5000
settings = ApplicationSettings()
CLIENT_ID = settings.nightbot_client_id
CLIENT_SECRET = settings.nightbot_client_secret
REDIRECT_URI = f"http://localhost:{port}/callback"

AUTH_BASE = "https://api.nightbot.tv/oauth2/authorize"
TOKEN_URL = "https://api.nightbot.tv/oauth2/token"
CURRENT_SONG_URL = "https://api.nightbot.tv/1/song_requests/queue"
SCOPE = ["song_requests_queue"]

token_storage = {}
if token_path.exists():
    try:
        token_storage["token"] = json.loads(token_path.read_text(encoding="utf-8"))
    except:
        pass


app = FastAPI()

templates = Jinja2Templates(directory="templates")

# In production, store per-user in DB


@app.get("/login")
def login():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    authorization_url, state = oauth.authorization_url(AUTH_BASE)

    token_storage["state"] = state
    return RedirectResponse(authorization_url)


@app.get("/callback")
async def callback(code: str):
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=token_storage.get("state"))
    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        code=code,
    )
    token_storage["token"] = token
    token_path.write_text(json.dumps(token, indent=4), encoding="utf-8")
    return RedirectResponse("/current-song-page.html")


@app.get("/current-song")
def current_song():
    token = token_storage.get("token")

    if not token or token["expires_at"] < int(datetime.now(timezone.utc).timestamp()):
        return RedirectResponse("/login")

    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }

    r = requests.get(CURRENT_SONG_URL, headers=headers)
    response = r.json()
    if response["_currentSong"] is None:
        return {
        "thumbnail_url": "",
        "title": "",
        "user": "",
    }

    show_artist = settings.show_artist is not None and response["_currentSong"]["track"]["artist"].lower() not in response["_currentSong"]["track"]["title"].lower()

    title = f"{response["_currentSong"]["track"]["artist"]} - {response["_currentSong"]["track"]["title"]}" if show_artist else response["_currentSong"]["track"]["title"]

    return {
        "thumbnail_url": response["_currentSong"]["track"]["thumbnailUrl"],
        "title": title,
        "user": response["_currentSong"]["user"]["displayName"],
    }


@app.get("/current-song-page.html")
def current_song_page(request: Request):
    token = token_storage.get("token")

    if not token:
        return RedirectResponse("/login")

    return templates.TemplateResponse(request, "thumbnail.html", {
        "stats_url": f"http://localhost:{port}/current-song",
    }
                                      )


if __name__ == '__main__':
    uvicorn.run(app, port=port)
