import json
import os


def sanitize_lyrics(lyrics):
    """
    Remove the "Contributors" and "Embed" sections from the lyrics and remove the lyrics if they are shorter than 300 words.

    Parameters:
    ----------
    lyrics: str
        Lyrics of a song.

    Returns:
    -------
    str
        Lyrics without the "Contributors" and "Embed" sections and without the lyrics if they are shorter than 300 words.
    """

    # Remove the "Contributor(s)" section from the lyrics if it exists
    if "Contributor" in lyrics:
        try:
            lyrics = lyrics.split("\n", 1)[1].strip()
        except IndexError:
            return ""

    # Remove the "Embed" section from the lyrics if it exists
    if "Embed" in lyrics:
        try:
            lyrics = lyrics[::-1].split("\n", 1)[1].strip()[::-1]
        except IndexError:
            return ""

    # Remove the lyrics if they are shorter than 300 words
    if len(lyrics.split()) < 300:
        return ""

    return lyrics


def sanitize_part_of_path(name):
    """
    Remove forbidden characters from the path.

    Parameters:
    ----------
    name: str
        Name to sanitize.

    Returns:
    -------
    str
        Name without forbidden characters.
    """

    # List of forbidden characters in Windows paths
    forbidden_chars = [
        "\\",
        "/",
        ":",
        "*",
        "?",
        '"',
        "<",
        ">",
        "|",
    ]

    # If longer than 100 characters, truncate the name to 100 characters
    if len(name) > 100:
        name = name[:100]

    # Replace forbidden characters with "_"
    for char in forbidden_chars:
        name = name.replace(char, "_")

    # Remove leading and trailing whitespaces, dots, commas, tabs, newlines and carriage returns
    return name.strip(" .,\t\n\r")


def get_one_album(genius, current_path, artist, album_name):
    """
    Get the lyrics of all the songs in an album and save them in text files.

    Parameters:
    ----------
    genius: Genius
        Genius API client.
    current_path: str
        Path of the current folder.
    artist: str
        Name of the artist.
    album_name: str
        Name of the album.

    Returns:
    -------
    None
    """

    # Search for the album on Genius
    album = genius.search_album(name=album_name, artist=artist, get_full_info=False)

    # If the album is not found, print a message and return
    if album is None:
        print(f"No album found for {artist} - {album_name}")
        return

    # Get the JSON representation of the album
    album_json = json.loads(album.to_json())

    # Get the artist name and album name
    album_artist_name = album_json["artist"]["name"]

    # Sanitize the artist name to use it in the path
    album_artist_name_sanitized = sanitize_part_of_path(album_artist_name)

    # Create the preliminary path to save the lyrics of the album songs in the format "lyrics/artist_name"
    album_songs_path = os.path.join(current_path, "lyrics", album_artist_name_sanitized)

    # Create the directory to save the lyrics of the album if it does not exist
    if not os.path.exists(album_songs_path):
        os.makedirs(album_songs_path)

    # Save the lyrics of each song in the album
    for song_json in album_json["tracks"]:
        # Get the number of the song in the album and skip the song if the number is not available
        song_number = song_json["number"]
        if song_number is None:
            continue

        # Get the title of the song and sanitize it to use it in the path
        song_title = song_json["song"]["title"]
        song_title_sanitized = sanitize_part_of_path(song_title)

        # Get the lyrics of the song and sanitize them
        song_lyrics = song_json["song"]["lyrics"]
        song_lyrics_sanitized = sanitize_lyrics(song_lyrics)

        # If the lyrics are empty, skip the song
        if song_lyrics_sanitized == "":
            continue

        # Extend the preliminary path to save the lyrics of the song in the format "lyrics/artist_name/song_title.txt"
        song_lyrics_path = os.path.join(album_songs_path, song_title_sanitized + ".txt")
        with open(song_lyrics_path, "w", encoding="utf-8") as f:
            f.write(song_lyrics_sanitized)

        print(f"{album_artist_name} - {song_title} lyrics saved in {song_lyrics_path}")


def get_artists_top_songs(genius, current_path, artist_name, max_songs, sort):
    """
    Get the top songs of an artist and save the lyrics of each song in a text file.

    Parameters:
    ----------
    genius: Genius
        Genius API client.
    current_path: str
        Path of the current folder.
    artist_name: str
        Name of the artist.
    max_songs: int
        Maximum number of songs to get.
    sort: str
        Sort the songs by "popularity" or "title".

    Returns:
    -------
    None
    """

    # Search for the artist on Genius and get the top songs
    artist = genius.search_artist(
        artist_name=artist_name, max_songs=max_songs, sort=sort
    )

    # If the artist is not found, print a message and return
    if artist is None:
        print(f"No artist found for {artist_name}")
        return

    # Get the JSON representation of the artist
    artist_json = json.loads(artist.to_json())

    # Get the name of the artist and sanitize it to use it in the path
    artist_name = artist_json["name"]
    artist_name_sanitized = sanitize_part_of_path(artist_name)

    # Create the preliminary path to save the lyrics of the songs in the format "lyrics/artist_name"
    artist_songs_path = os.path.join(current_path, "lyrics", artist_name_sanitized)

    # Create the directory to save the lyrics of the artist songs if it does not exist
    if not os.path.exists(artist_songs_path):
        os.makedirs(artist_songs_path)

    # Save the lyrics of each song in the top songs
    for song_json in artist_json["songs"]:
        # Get the title of the song and sanitize it to use it in the path
        song_title = song_json["title"]
        song_title_sanitized = sanitize_part_of_path(song_title)

        # Get the lyrics of the song and sanitize them
        song_lyrics = song_json["lyrics"]
        song_lyrics_sanitized = sanitize_lyrics(song_lyrics)

        # If the lyrics are empty, skip the song
        if song_lyrics_sanitized == "":
            continue

        # Extend the preliminary path to save the lyrics of the song in the format "lyrics/artist_name/song_title.txt"
        song_lyrics_path = os.path.join(
            artist_songs_path, song_title_sanitized + ".txt"
        )

        # Save the lyrics of the song in a text file
        with open(song_lyrics_path, "w", encoding="utf-8") as f:
            f.write(song_lyrics_sanitized)

        print(f"{artist_name} - {song_title} lyrics saved in {song_lyrics_path}")


def get_one_song(genius, current_path, artist, title):
    """
    Get the lyrics of a single song and save them in a text file.

    Parameters:
    ----------
    genius: Genius
        Genius API client.
    current_path: str
        Path of the current folder.
    artist: str
        Name of the artist.
    title: str
        Title of the song.

    Returns:
    -------
    None
    """

    # Search for the song on Genius
    song = genius.search_song(title=title, artist=artist)

    # If the song is not found, print a message and return
    if song is None:
        print(f"No song found for {artist} - {title}")
        return

    # Get the JSON representation of the song
    song_json = json.loads(song.to_json())

    # Get the artist name and sanitize it to use it in the path
    song_artist_name = song_json["artist_names"]
    song_artist_name_sanitized = sanitize_part_of_path(song_artist_name)

    # Create the preliminary path to save the lyrics of the song in the format "lyrics/artist_name"
    single_songs_path = os.path.join(current_path, "lyrics", song_artist_name_sanitized)

    # Create the directory to save the lyrics of the songs if it does not exist
    if not os.path.exists(single_songs_path):
        os.makedirs(single_songs_path)

    # Get the title of the song and sanitize it to use it in the path
    song_title = song_json["title"]
    song_title_sanitized = sanitize_part_of_path(song_title)

    # Get the lyrics of the song and sanitize them
    song_lyrics = song_json["lyrics"]
    song_lyrics_sanitized = sanitize_lyrics(song_lyrics)

    # If the lyrics are empty, print a message and return
    if song_lyrics_sanitized == "":
        print(f"No lyrics found for {song_artist_name} - {song_title}")
        return

    # Extend the preliminary path to save the lyrics of the song in the format "lyrics/artist_name/song_title.txt"
    song_lyrics_path = os.path.join(single_songs_path, song_title_sanitized + ".txt")
    with open(song_lyrics_path, "w", encoding="utf-8") as f:
        f.write(song_lyrics_sanitized)

    print(f"{song_artist_name} - {song_title} lyrics saved in {song_lyrics_path}")
