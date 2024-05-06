"""
    This file contains functions to get the song features of a song using the Spotify API

    Functions:
        get_token(): This function gets the token for accessing the Spotify API
        get_auth_header(token): This function sets the authorization header for the API request
        api_request(url, headers, params=None, data=None): This function generates API request using custom url, parameters and data
        get_mul_artists_genres(token, artist_id_list): This function gets multiple artists' info using a list of artist IDs
        get_track_feature_info(track_features): This function parses a dictionary containing track features and returns the features needed from this dictionary
        get_song_features(token, track_id): This function gets the song features of a song using the Spotify API

    Input:
        token: token for accessing the Spotify API
        track_id: track ID of the song

    Outputs:
        Function specific

    Usage:
        - `from src.utils.get_song_features import get_song_features`
        - No other direct usage
"""

# Import libraries
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import time

# Load .env file
load_dotenv()

# Load CLIENT_ID and CLIENT_SECRET for accessing the API
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Get token using client credentials
def get_token():
    
    """
        This function gets the token for accessing the Spotify API
        
        Args:
            None

        Returns:
            str: Returns the token for accessing the Spotify API
    """

    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    # Base url to be used
    url = "https://accounts.spotify.com/api/token"

    # Declare headers
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type":"application/x-www-form-urlencoded"
        }
    
    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)

    json_result = json.loads(result.content)

    token = json_result["access_token"]

    return token


# Set Authorization
def get_auth_header(token):

    return {"Authorization":"Bearer " + token}

# Function to generate API request using custom url, parameters and data
def api_request(url, headers, params=None, data=None):

    """
        Create a function to generate API request using custom url, parameters and data

        Args:
            param1 (str): url of the request
            param2 (str): declared header
            param3 (dict): parameters for the api request
            param4 (dict): additional data to pass

        Returns:
            dict: return dict format of response. If response empty, return error
    """

    retry = True

    while retry:

        response = get(url, headers=headers, params=params, data=data)

        # Status Code == 200 means successful request 
        if response.status_code == 200:
            return response
        
        # Time out error - API Request limit exceeded
        elif response.status_code == 429:

            retry_after = int(response.headers.get('Retry-After'))
            print(f"Rate limit exceeded. Wait for {retry_after} seconds before trying again.")
            return 'Try again'
        
        else:

            print(f"Request failed with error {response.status_code}: {response.text}")
            
            return response.status_code


def get_mul_artists_genres(token, artist_id_list):
    """
        This function gets multiple artists' info using a list of artist IDs

        Args:
            param1 (str): token
            param2 (list): comma separated values of artist IDs in a list

        Returns:
            list: Returns a nested list of genres (list format) for each artist ID in 
                corresponding index
    """
    
    # Declare list to be returned 
    genre_artist_list = []

    url = f"https://api.spotify.com/v1/artists/?ids={artist_id_list}"

    headers = get_auth_header(token)

    playlist_result = api_request(url, headers=headers)

    if playlist_result is None or playlist_result == 'Try again':

        return ("Failed to retrieve playlist information.")

    else:

        json_result = json.loads(playlist_result.content)

        # Get dictionary where genres are located
        genres = json_result["artists"]

        # for each entry in dictionary, get genre for each artist
        for genre in genres:

            genre_artist = genre["genres"]

            genre_artist_list.append(genre_artist)

        return genre_artist_list


def get_track_feature_info(track_features):
    """
        This function parses a dictionary containing track features and returns 
        the features needed from this dictionary

        Args:
            param1 (dict): track_features containing all info 

        Returns:
            dict: Dictionary containing all the features needed for the track

    """
    
    # Declare dictionary to be returned
    track_feature_info = {
        "id" : None, 
        "danceability": None,
        "energy": None,
        "key": None,
        "loudness": None,
        "mode": None,
        "speechiness": None,
        "acousticness": None,
        "instrumentalness": None,
        "liveness": None,
        "valence": None,
        "tempo": None,
        "duration_ms": None,
        "time_signature": None
        }
    
    try: 

        # Parse all the necessary information
        track_feature_info["id"] = track_features["id"]
        track_feature_info["danceability"] = track_features["danceability"]
        track_feature_info["energy"] = track_features["energy"]
        track_feature_info["key"] = track_features["key"]
        track_feature_info["loudness"] = track_features["loudness"]
        track_feature_info["mode"] = track_features["mode"]
        track_feature_info["speechiness"] = track_features["speechiness"]
        track_feature_info["acousticness"] = track_features["acousticness"]
        track_feature_info["instrumentalness"] = track_features["instrumentalness"]
        track_feature_info["liveness"] = track_features["liveness"]
        track_feature_info["valence"] = track_features["valence"]
        track_feature_info["tempo"] = track_features["tempo"]
        track_feature_info["duration_ms"] = track_features["duration_ms"]
        track_feature_info["time_signature"] = track_features["time_signature"]

        return track_feature_info
    
    except:

        return None

    


def get_track_info(track):
    """
        This function parses a dictionary containing track information and returns 
        them needed from this dictionary

        Args:
            param1 (dict): track_features containing all info 

        Returns:
            dict: Dictionary containing all the information needed for the track

    """
    
    # Declare dictionary to be returned
    tracks = {
        "id" : None,
        "name" : None, 
        "artist id" : None,
        "artists" : [],
        "artist genre" : [],
        "album type" : None,
        "album id" : None,
        "album name" : None,
        "album release date" : None,
        "duration_ms" : None,
        "popularity" : None,
    }

    # Parse all the required track features
    tracks["id"] = track["id"]
    tracks["name"]= track["name"]
    tracks["popularity"] = track["popularity"]
    tracks["duration_ms"] = track["duration_ms"]
    tracks["album type"] = track["album"]["album_type"]
    tracks["album id"] = track["album"]["id"]
    tracks["album name"] = track["album"]["name"]
    tracks["album release date"] = track["album"]["release_date"]

    # Get artist info separately
    artists = track["artists"]

    artist_name_list = []
    artist_id_list = []

    # Extract artist info for name and id
    for artist in artists:

        artist_name_list.append(artist["name"])
        artist_id_list.append(artist["id"])

    tracks["artist id"] = artist_id_list
    tracks["artists"] = artist_name_list

    return tracks

def get_songs_by_playlists(token, playlist_id):
    """
        This function parses a playlist ID and returns track IDs for the
        playlist

        Args:
            param1 (str): token
            param2 (str): playlist id

        Returns:
            dict: Dictionary containing tracks for the playlist id
    """
    headers = get_auth_header(token)

    # Initialize dictionary to be returned
    playlist_info_dict = {
        'tracks' : None
        }

    offset = 0
    track_ids = []

    # While loop to adjust for request limit and keep adding offset
    while True:

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit=100"
        headers = get_auth_header(token)

        playlist_result = api_request(url, headers = headers)

        if playlist_result is None or playlist_result == 'Try again':

            print("Failed to retrieve playlist information.")

        else:

            playlist= json.loads(playlist_result.content)

            # Get track info
            playlist_tracks = playlist["items"]

            for item in playlist_tracks:
                try:
                    track_id = item['track']['id']
                    track_ids.append(track_id)
                except:
                    pass

            # If more tracks exist, offset += 100
            if playlist['next']:

                offset += 100
            else:

                break
            
    playlist_info_dict['tracks'] = track_ids
    
    return playlist_info_dict     

def get_mul_tracks(token, playlist_id, playlist_tracks):
    """
        This function takes a playlist_id and a list of playlist
        tracks and returns track information for each track from the playlist
        in a dictionary

        Args:
            param1 (str): token
            param2 (str): playlist id
            param3 (dict): dictionary containing all track IDs as a value for the key: 'tracks'

        Returns:
            dict: Dictionary two key-value pairs
            {
                'playlist id' : playlist id,
                'tracks' : []
            }
    """
    track_id_list = playlist_tracks['tracks']
    track_id_list = list(filter(lambda x: x is not None, track_id_list))
    try:
        if len(track_id_list) > 50:
            params = {
                'ids' : ','.join(track_id_list[:50]), # Get first 50 tracks
                'market' : 'US'
            }
        else:
            params = {
                'ids' : ','.join(track_id_list[:len(track_id_list)]), # Get first 50 tracks
                'market' : 'US'
            }
    
    except:

        print(track_id_list)


    # Declare dictionary to be returned
    playlist_track_info_dict = {
        'playlist id' : playlist_id,
        'tracks' : []
    }

    tracks_list = []
    artist_ids_list = []

    url = f"https://api.spotify.com/v1/tracks"
    headers = get_auth_header(token)

    playlist_result = api_request(url, headers=headers, params=params)

    if playlist_result is None or playlist_result == 'Try again':

        print("Failed to retrieve playlist information.")

    else:
        
        tracks = json.loads(playlist_result.content)

        track_data = tracks['tracks']

        track_id_length = len(track_id_list)

        # Get all artist IDs and store it in artist id list
        for track in track_data:
            
            artist_ids = track["album"]["artists"][0]["id"]
            artist_ids_list.append(artist_ids)

        # get list into correct format to be sent in url request
        artist_ids_list = ','.join(artist_ids_list)

        # extract genres for each artist
        genre_ids = get_mul_artists_genres(token, artist_ids_list)

        for index, track in enumerate(track_data):

            track_info = get_track_info(track)

            genre = genre_ids[index]

            track_info["artist genre"] = genre

            tracks_list.append(track_info)

        # Set offset to adjust for limit rate
        offset = 50
        
        # Use this section of code to get track info for more than 50 tracks in a playlist
        while offset < track_id_length: 

            artist_ids_list = []

            # Get track ids in correct format to be sent in url request
            params['ids'] = ','.join(track_id_list[offset:offset+50])

            playlist_result = api_request(url, headers=headers, params=params)

            if playlist_result is None or playlist_result == 'Try again':

                print("Failed to retrieve playlist information.")

            else:   
                
                tracks = json.loads(playlist_result.content)

                track_data = tracks['tracks']

                for track in track_data:

                    artist_ids = track["album"]["artists"][0]["id"]
                    artist_ids_list.append(artist_ids)

                artist_ids_list = ','.join(artist_ids_list)

                genre_ids = get_mul_artists_genres(token, artist_ids_list)

                for index, track in enumerate(track_data):

                    track_info = get_track_info(track)

                    genre = genre_ids[index]

                    track_info["artist genre"] = genre

                    tracks_list.append(track_info)

            offset += 50

    playlist_track_info_dict['playlist id'] = playlist_id
    playlist_track_info_dict['tracks'] = tracks_list

    return playlist_track_info_dict


def get_mul_tracks_features(token, playlist_id, playlist_tracks):
    """
        This function takes a playlist_id and a list of playlist
        tracks and returns track features for each track from the playlist
        in a dictionary

        Args:
            param1 (str): token
            param2 (str): playlist id
            param3 (dict): dictionary containing all track IDs as a value for the key: 'tracks'

        Returns:
            dict: Dictionary two key-value pairs
            {
                'playlist id' : playlist id,
                'tracks' : []
            }
    """
    # Initialize dictionary to be returned
    playlist_track_feature_info_dict = {
        'playlist id' : playlist_id,
        'tracks' : []
    }

    track_id_list = playlist_tracks['tracks']

    track_id_list = list(filter(lambda x: x is not None, track_id_list))

    try: 
        params = {
            'ids' : ','.join(track_id_list[:100]), # Get first 100 tracks
        }

    except:
        params = {
            'ids' : ','.join(track_id_list[:len(track_id_list)]), # Get first 100 tracks
        }

    tracks_features_list = []
    
    url = f"https://api.spotify.com/v1/audio-features"
    headers = get_auth_header(token)

    playlist_result = api_request(url, headers=headers, params=params)

    if playlist_result is None or playlist_result == 'Try again':

        print("Failed to retrieve playlist information.")

    else:
        
        tracks = json.loads(playlist_result.content)

        track_data = tracks['audio_features']

        track_id_length = len(track_id_list)
        
        for track in track_data:
            
            # Get track features 
            track_info = get_track_feature_info(track)

            tracks_features_list.append(track_info)
        
        # Use offset 100 to adjust for the limit
        offset = 100
        
        # Use this section of code to adjust for more than 100 tracks
        while offset < track_id_length:

            # Keep adjusting offset
            params['ids'] = ','.join(track_id_list[offset:offset+100])

            playlist_result = api_request(url, headers=headers, params=params)

            if playlist_result is None or playlist_result == 'Try again':

                print("Failed to retrieve playlist information.")

            else:   
                
                tracks = json.loads(playlist_result.content)

                
                track_data = tracks['audio_features']

                for track in track_data:
                    
                    # Get track features 
                    try : 
                        track_info = get_track_feature_info(track)

                        if track_info == None:
                            pass
                        
                        else:

                            tracks_features_list.append(track_info)
                    
                    except:
                        pass
                
            offset += 100

    playlist_track_feature_info_dict['playlist id'] = playlist_id
    playlist_track_feature_info_dict['tracks'] = tracks_features_list

    return playlist_track_feature_info_dict


def concatenate_playlist_info(playlist_track_info, playlist_features_info):
    """
        This function takes two input dictionaries, each containing information of 
        tracks from a playlist and containing features of tracks from the same playlist.
        It concatenates the entries for each index and returns a dictionary

        Args:
            param1 (str): token
            param2 (dict): dictionary containing information on all tracks from playlist id
            param3 (dict): dictionary containing features on all tracks from playlist id

        Returns:
            dict: Dictionary two key-value pairs
            {
                'playlist id' : playlist id,
                'tracks' : []
            }
    """

    # Initialize dictionary to be returned
    playlist_tracks_all_info_dict = {
        "playlist id" : None,
        "tracks" : []
        }
    
    track_info_id = playlist_track_info["playlist id"]
    playlist_tracks_list = playlist_track_info["tracks"]

    track_features_id = playlist_features_info["playlist id"]    
    playlist_tracks_features_list = playlist_features_info["tracks"]

    # Check if concatenation is possible
    if (track_info_id == track_features_id) and len(playlist_tracks_features_list) == len(playlist_tracks_list):

        playlist_tracks_all_info_dict["playlist id"] = track_info_id

        playlist_tracks_list = playlist_track_info["tracks"]
        playlist_tracks_features_list = playlist_features_info["tracks"]

        for i in range(len(playlist_tracks_list)):

            try:
                track_dict = {**playlist_tracks_list[i], **playlist_tracks_features_list[i]}

                playlist_tracks_all_info_dict["tracks"].append(track_dict)

            except:

                pass

    return playlist_tracks_all_info_dict
