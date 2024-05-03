from dotenv import load_dotenv, find_dotenv
from lyricsgenius import Genius
import pandas as pd
import os

from download_lyrics_functions import get_one_album, get_one_song, get_artists_top_songs


# Load the environment variables from the .env file
load_dotenv(find_dotenv())

# Genius API client with some custom settings
genius = Genius(
    access_token=os.getenv("GENIUS_TOKEN"),
    timeout=5,
    sleep_time=0.2,
    retries=100,
)
genius.remove_section_headers = True

current_path = os.path.dirname(os.path.abspath(__file__))

########################################
# Download lyrics for albums
########################################

# Get popular albums from a CSV file and get the lyrics of all the songs of each album
albums_path = os.path.join(current_path, "datasets", "popular_albums_dataset.csv")
albums = pd.read_csv(albums_path)

# Get the number of albums
max_albums = len(albums)

# Get the lyrics of all the albums using the get_one_album function
for i, row in albums.iterrows():
    print(f"Getting lyrics for album {i + 1} of {max_albums}")
    artist = row["Artist"]
    album_name = row["Album"]
    get_one_album(genius, current_path, artist, album_name)

########################################
# Download lyrics for songs
########################################

# Get popular songs from a CSV file and get the lyrics of all the songs
songs_path = os.path.join(current_path, "datasets", "popular_songs_dataset.csv")
songs = pd.read_csv(songs_path)

# Get the number of songs
max_songs = len(songs)

# Get the lyrics of all the songs using the get_one_song function
for i, row in songs.iterrows():
    print(f"Getting lyrics for song {i + 1} of {max_songs}")
    artist = row["Artist"]
    title = row["Title"]
    get_one_song(genius, current_path, artist, title)

########################################
# Download lyrics for artists top songs
########################################

# Get popular artists from a CSV file and get the lyrics of the top 50 songs of each artist
artists_path = os.path.join(current_path, "datasets", "popular_artists_dataset.csv")
artists = pd.read_csv(artists_path)

# Get the number of artists
max_artists = len(artists)

# Get the lyrics of the top 50 songs of each artist using the get_artists_top_songs function
for i, row in artists.iterrows():
    print(f"Getting lyrics for artist {i + 1} of {max_artists}")
    artist_name = row["Artist"]
    get_artists_top_songs(
        genius, current_path, artist_name, max_songs=50, sort="popularity"
    )
