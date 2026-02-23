import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import requests
from starlette.templating import Jinja2Templates

from songrequest.settings import ApplicationSettings

load_dotenv()

port = 5000
settings = ApplicationSettings()
CLIENT_ID = settings.nightbot_client_id
CLIENT_SECRET = settings.nightbot_client_secret
REDIRECT_URI = f"http://localhost:{port}/callback"

AUTH_BASE = "https://api.nightbot.tv/oauth2/authorize"
TOKEN_URL = "https://api.nightbot.tv/oauth2/token"
CURRENT_SONG_URL = "https://api.nightbot.tv/1/song_requests/queue"
SCOPE = ["song_requests_queue"]
app = FastAPI()

templates = Jinja2Templates(directory="templates")

# In production, store per-user in DB
token_storage = {}


@app.get("/login")
def login():
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    authorization_url, state = oauth.authorization_url(AUTH_BASE)

    token_storage["state"] = state
    print(authorization_url)
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
    return RedirectResponse("/current-song-page.html")


@app.get("/current-song")
def current_song():
    token = token_storage.get("token")

    if not token:
        return RedirectResponse("/login")

    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }

    r = requests.get(CURRENT_SONG_URL, headers=headers)
    response = r.json()

    return {
        "thumbnail_url": response["_currentSong"]["track"]["thumbnailUrl"],
        "title": f"{response["_currentSong"]["track"]["artist"]} - {response["_currentSong"]["track"]["title"]}",
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
