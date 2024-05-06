'''
This file is used to create the detailed playlist information in csv format

input: a link to a playlist which is public

output: a csv file with containing the playlist information

usage: python test_playlist_to_csv.py

'''

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import time
import pandas as pd
from dotenv import load_dotenv
from feature_engineering.get_song_features import get_songs_by_playlists, get_mul_tracks \
                                  , get_mul_tracks_features, concatenate_playlist_info


dotenv_path = 'utils/.env'
load_dotenv(dotenv_path ,verbose=False)

# Load CLIENT_ID and CLIENT_SECRET for accessing the API
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")



# Get token using client credentials
def get_token():

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
            
            return None
        

def parse_playlist_link(link):
    """
    Function to extract playlist id from a copied spotify playlist link

    Args:
        param1 (str): playlist link copied from spotify

    Returns:
        str: returns unique playlist id, if not returns error
    """

    if 'open.spotify.com/playlist/' in link:

        if '?' in link:
        
            playlist_link = link.split('?', 1)[0]
            playlist_link = playlist_link[-22:]

            return playlist_link
            
        else:
        
            playlist_link = link[-22:]

            return playlist_link

    print('Incorrect Link!')
    return 'Incorrect Link!'


def get_playlist_to_json(playlist_link):
    """
    Function to use playlist link and convert the features of all tracks into a json

    Args:
        param1 (str): playlist link copied from spotify

    Returns:
        str: returns json file containing track information for all tracks in the playlist
    """
    status = 200
    token = get_token()

    playlist_id = parse_playlist_link(playlist_link)

    if playlist_id == 'Incorrect Link!':
        status = 400

    if playlist_id != 'Incorrect Link!':

        try: 

            playlist_tracks = get_songs_by_playlists(token, playlist_id)

            time.sleep(3)

            playlist_tracks_info = get_mul_tracks(token, playlist_id, playlist_tracks)

            time.sleep(3)

            playlist_tracks_features_info = get_mul_tracks_features(token, playlist_id, playlist_tracks)

            playlist_tracks_json = concatenate_playlist_info(playlist_tracks_info, playlist_tracks_features_info)
        
        except:
            
            playlist_tracks_json = {}

    else:

        playlist_tracks_json = {}

    return playlist_tracks_json, status

def get_json_to_csv(json_obj):

    """
    Function that takes a json file containing information of a playlist and cleans it
    

    Args:
        param1 (str): json file 

    Returns:
        str: returns csv format of json after performing data cleaning
    """

    try: 
        playlist_id = json_obj['playlist id']
        tracks = json_obj['tracks']

        df = pd.DataFrame(tracks)

        df.dropna(subset=["id", "name", "artist id", "artists", "artist genre"], inplace=True)
        df.drop_duplicates(subset=["id"], inplace=True)

        df['artist id'] = df['artist id'].apply(lambda x: ','.join(set(y for y in x)))
        df['artists'] = df['artists'].apply(lambda x: ','.join(set(y for y in x)))
        df['artist genre'] = df['artist genre'].apply(lambda x: ','.join(set(y for y in x)))

        df['artist id'] = df['artist id'].str.replace('"', "'")
        df['artists'] = df['artists'].str.replace('"', "'")
        df['artist genre'] = df['artist genre'].str.replace('"', "'")

        df['name'] = df['name'].apply(lambda str: str.lower())
        df['artists'] = df['artists'].apply(lambda str: str.lower())
        df['artist genre'] = df['artist genre'].apply(lambda str: str.lower())
        df['album name'] = df['album name'].apply(lambda str: str.lower())

        df['album release date'] = df['album release date'].apply(lambda x: pd.to_datetime(x, errors='coerce').year)

        new_cols = ['id', 'name', 'artist_id', 'artists', 'artist_genre', 'album_type',
            'album_id', 'album_name', 'album_release_date', 'duration_ms',
            'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode',
            'speechiness', 'acousticness', 'instrumentalness', 'liveness',
            'valence', 'tempo', 'time_signature']

        df.columns = new_cols

        df.dropna(subset=["id", "name", "artist_id", "artists", "artist_genre"], inplace=True)

        return playlist_id, df

    except:

        return 'Fatal Error!'


def playlist_to_csv(link):
    """
    Function that takes a playlist from the app and process it to get the features csv
    

    Args:
        param1 (str): playlist link 

    Returns:
        CSV of the playlist feature in the directory and a message stating done to the application
    """

    start_time = time.time()
    
    playlist_link = link
    
    playlist_tracks_json, status = get_playlist_to_json(playlist_link)

    if status == 400:
        
        return "no playlist", 400

    playlist_id, playlist_tracks_df = get_json_to_csv(playlist_tracks_json)

    #playlist_name = playlist_id + '_' + 'data.csv'
    playlist_name = 'data/playlist_data.csv'
    playlist_tracks_df.to_csv(playlist_name, index = False)

    end_time = time.time()
    runtime = end_time - start_time


    print(f"Runtime: {runtime:.2f} seconds")
    print('Done!')

    return playlist_name , 200
