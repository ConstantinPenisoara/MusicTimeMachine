from bs4 import BeautifulSoup
import requests
import os
import pprint
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify credentials
CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('SPOTIPY_REDIRECT_URI')

# Prompting the user for the desired date
desired_date = input("Which year would you like to travel to? Type the data in this format YYYY-MM-DD?:\n")

# Scraping billboard.com for the top 100 at the desired date
response = requests.get(f"https://www.billboard.com/charts/hot-100/{desired_date}/")
year = desired_date.split("-")[0]

billboard_webpage = response.text
soup = BeautifulSoup(billboard_webpage, "html.parser")

chart = soup.find_all(name="h3")
chart1 = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-"
                                         "23@tablet lrv-u-font-size-16 u-line-height-125 "
                                         "u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 "
                                         "u-max-width-230@tablet-only u-letter-spacing-0028@tablet")
chart2 = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 "
                                         "lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 "
                                         "u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 "
                                        "u-max-width-230@tablet-only")
# Compiling the top 100 songs
top100 = []
for song in chart1:
    top100.append(song.get_text().strip())
for song in chart2:
    top100.append(song.get_text().strip())

# Authentication with spotify and getting the user ID
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt",
        username="Costi",
    )
)
user_id = sp.current_user()["id"]

spotify_song_URIs = []

# Populating spotify_song_URIs list with the URI's of the songs in the top 100
for n in top100:
    try:
        track = sp.search(q=f'track:{n} year:{year}', type='track', market="US", limit=1)
        spotify_song_URIs.append(track['tracks']['items'][0]['uri'])
    except IndexError:
        continue

# Creating the Spotify playlist
my_playlist = sp.user_playlist_create(user=user_id, name=f'{desired_date} Billboard 100', public=False,
                                      description="Top 100 songs at given date")

# Populate the playlist with the tracks in the top 100
playlist_id = my_playlist['id']
sp.playlist_add_items(playlist_id=playlist_id, items=spotify_song_URIs, position=None)
