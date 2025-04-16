import base64
import math
import requests
from dotenv import load_dotenv
from os import getenv


class Spotify:
    def __init__(self, playlist_id, market="NO") -> None:
        self.playlist_id = playlist_id
        self.market = market

    def _get_bearer(self):
        token_url = "https://accounts.spotify.com/api/token"
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        response = requests.post(
            token_url,
            headers={ 
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        )
        return response.json().get("access_token")

    def _get_total(self, token):
        total = requests.get(f"https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks?market={self.market}&fields=total", headers={"Authorization": f"Bearer {token}"})
        return total.json().get("total")

    def _get_playlist(self, token, limit=50, offset=0):
        response = requests.get(f"https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks?market={self.market}&fields=items%28track%28name%2Calbum.artists.name%29%29&limit={limit}&offset={offset}", headers={"Authorization": f"Bearer {token}"})
        return response.json()["items"]

    def _export_to_file(self, playlist):
        with open('songs.txt', "w") as file:
            for song in playlist:
                artists = [artist["name"] for artist in song["track"]["album"]["artists"]]
                artists = ", ".join(artists)
                file.write(f"{artists} - {song['track']['name']}\n")

    def start(self):
        token = self._get_bearer()
        total = self._get_total(token)
        limit = 50
        offset = 0
        playlist = list()
        for batch in range(1, math.ceil(total/50)+1):
            playlist.extend(self._get_playlist(token, limit, offset))
            offset = limit * batch
        self._export_to_file(playlist)


if "__main__" == __name__:
    load_dotenv()
    key = "client_id"
    client_id = getenv(key)
    key = "client_secret"
    client_secret = getenv(key)
    key = "playlist_id"
    playlist_id = getenv(key)
    yeppers = Spotify(playlist_id)
    yeppers.start()
