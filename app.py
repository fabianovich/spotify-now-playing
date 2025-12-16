import json
import os
import webbrowser
from urllib.parse import urlencode

import requests

TOKEN_FILE = "spotify_tokens.json"
CREDENTIALS = "credentials.json"


def save_tokens(access_token, refresh_token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access_token": access_token, "refresh_token": refresh_token}, f)


def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None


def load_credentials(type):
    if os.path.exists(CREDENTIALS):
        with open(CREDENTIALS, "r") as f:
            return json.load(f)[type]
    return None


def refresh_access_token(refresh_token):
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    data = response.json()
    return data["access_token"]


def get_initial_tokens():
    auth_params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "user-read-currently-playing",
    }

    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"
    print("auth in browser...")
    webbrowser.open(auth_url)

    auth_code = input("\npaste url code:  ")

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )

    data = response.json()
    save_tokens(data["access_token"], data["refresh_token"])
    return data["access_token"]


CLIENT_ID = load_credentials("client_id")
CLIENT_SECRET = load_credentials("client_secret")
REDIRECT_URI = load_credentials("redirect_uri")
tokens = load_tokens()
if tokens and tokens.get("refresh_token"):
    print("using saved token")
    try:
        access_token = refresh_access_token(tokens["refresh_token"])
        save_tokens(access_token, tokens["refresh_token"])
    except:
        print("whuppss, getting new tokens")
        access_token = get_initial_tokens()
else:
    access_token = get_initial_tokens()

print("access token yay")

playing = requests.get(
    "https://api.spotify.com/v1/me/player/currently-playing",
    headers={"Authorization": f"Bearer {access_token}"},
)

if playing.status_code == 200 and playing.text:
    track = playing.json()
    song = track["item"]["name"]
    artist = track["item"]["artists"][0]["name"]
    print(f"\nsong: {song} by {artist}")
else:
    print("\no song playing")
