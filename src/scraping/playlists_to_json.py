"""
    This file is used to scrape the playlist details from the scraped playlist links folder.

    Input:
        Directory containing the playlist links for each genre
    
    Output:
        Directories containing JSON files for every playlist in each genre
    
    Usage:
        python3 scraping/playlists_to_json.py
"""

# Importing the required libraries
from dotenv import load_dotenv
import os
import shutil
import base64
from requests import post, get
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.get_song_features import get_songs_by_playlists, get_mul_tracks, get_mul_tracks_features, concatenate_playlist_info


# Set up the Spotify API credentials
dotenv_path = 'utils/.env'
load_dotenv(dotenv_path ,verbose=False)

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

    result = post(url, headers = headers, data = data)

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

# Create a dictionary of playlist links
def create_playlist_dict(folder_path):
    """
        Create a function that will create a dictionary of playlists for each genre txt file

        Args:
            param1 (str): path to the playlists txt folder
    
        Returns:
            dict: return dict format of playlists -> 
                    {key} : {value} -> genre : list of unique playlist ids
    """
    playlist_dict = {}

    for filename in os.listdir(folder_path):

        if filename.endswith('.txt'):

            file_path = os.path.join(folder_path, filename)

            with open(file_path, 'r') as f:

                playlists = []

                for line in f:

                    if 'https://open.spotify.com/playlist/' in line and len(line) == 57:

                        playlists.append(line[-23:].strip())
                    
                    else: 

                        playlists = []
                        
                        return "Wrong playlist folder for: " + line
                    
                playlist_dict[filename] = playlists
        
    return playlist_dict


# Get the playlist details
def get_user_playlists_to_json(filepath):
    """
        Create a function that will generate a folder with subfolders of genres, containing info on each playlist

        Args:
            param1 (str): path to where the json files will be stored
    
        Returns:
            dict: None
    """

    # Get all genre dictionaries and sort them using the names of genres
    playlist_link_dicts = create_playlist_dict(filepath)
    playlist_link_dicts = dict(sorted(playlist_link_dicts.items()))

    # keys_to_delete = list(playlist_link_dicts.keys())[:89]

    # for key in keys_to_delete:
    #     del playlist_link_dicts[key]
    
    # write code to save playlists for each genre
    for playlist_name, playlist_links in playlist_link_dicts.items():

        token = get_token()

        # extract genre name from the playlist name
        filename = playlist_name[:-14]
        filename = filename.replace(" ", "_")

        # make a new folder with the filename
        os.system("cd data/json/json_scraped/ && mkdir %s" %filename)

        # extract features for tracks in the playlist for each playlists
        for playlist_id in playlist_links:

            try: 

                playlist_tracks = get_songs_by_playlists(token, playlist_id)
            
                playlist_tracks_info = get_mul_tracks(token, playlist_id, playlist_tracks)

                playlist_tracks_features_info = get_mul_tracks_features(token, playlist_id, playlist_tracks)

                playlist_tracks_all_info = concatenate_playlist_info(playlist_tracks_info, playlist_tracks_features_info)

                with open("data/json/json_scraped" + "/" + filename  + "/" + filename + "_" + playlist_id + '.json', 'w', encoding='utf-8') as f:
                    json.dump(playlist_tracks_all_info, f, ensure_ascii=False, indent=4)

                print("Done!")

            except:
                
                print('failed at: ' + playlist_id + 'for ' + filename)
                
        # sleep the code so API requests doesn't encounter a timeout error
            time.sleep(5)
        
        time.sleep(5)

        print("Done for playlist: " +  filename)


if __name__ == "__main__":

    start_time = time.time()

    filename = 'json_scraped'
    os.system("cd data/json && mkdir %s" %filename)

    get_user_playlists_to_json("data/playlists")

    end_time = time.time()
    runtime = end_time - start_time
    print(f"Runtime: {runtime:.2f} seconds")
    print('Done!')
