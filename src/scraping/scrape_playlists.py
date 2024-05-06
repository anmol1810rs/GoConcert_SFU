"""
    This script scrapes the Spotify API for playlists that are user-owned and publicly available.

    Input:
        None

    Output:
        Text files containing the playlist details for each genre.

    Usage:
        python3 scraping/scrape_playlists.py
"""

# Importing the required libraries
from dotenv import load_dotenv
from requests import get, post
import time
import os
import json
import base64

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

def get_playlists(token):

    """
        Create a function to generate text files for numerous genres containing 60 playlists each

        Args:
            param1 (str): token
    
        Returns:
            None
    """
    
    # Create a list of genres
    genre_list = [  'acoustic', 'afrobeat', 'alt-country', 'alternatives', 'ambient',
                    'americana', 'avant-garde', 'ballads', 'blues', 'bollywood', 'brazilian',
                    'breakbeat', 'britpop', 'celtic', 'chamber', 'chanson francaise',
                    'children', 'chillout', 'classical', 'country', 'dance', 
                    'darkwave', 'death metal', 'deep house', 'disco', 'downtempo', 
                    'drone', 'dubstep', 'easy listening', 'electronic', 'emo', 
                    'experimental', 'folk', 'funk', 'fusion', 'garage', 'glitch',
                    'goa', 'gospel', 'grunge', 'hard rock', 'hardcore', 'hip hop',
                    'holiday', 'house', 'idm', 'indie', 'indie pop', 'industrial',
                    'instrumental', 'international', 'jazz', 'jungle', 'latin',
                    'lo-fi', 'medieval', 'metal', 'minimal', 'modern classical',
                    'new age', 'noise', 'nu-jazz', 'other', 'pop', 'post-punk',
                    'post-rock', 'power pop', 'progressive', 'psychedelic',
                    'punk', 'r and b', 'rap', 'reggae', 'religious', 
                    'renaissance', 'rock', 'rockabilly', 'romantic',
                    'shoegaze', 'singer-songwriter', 'ska', 'soul', 'soundtrack',
                    'space rock', 'stage and screen', 'surf', 'synthpop',
                    'techno', 'trance', 'trip hop', 'unknown', 'vocal', 'world']

    # Scrape the playlists for each genre
    for genre in genre_list:

        offset = 0
        user_playlists = []

        params = {
            'type': 'playlist',
            'limit': 50,
            'offset': 0
        }

        # Get the first 60 playlists
        while len(user_playlists) < 60:

                url = f'https://api.spotify.com/v1/search?q={genre}'

                headers = get_auth_header(token)

                # Make the API request and get the data
                playlist_result = api_request(url, headers=headers, params = params)

                if playlist_result is None or playlist_result == 'Try again':

                    return ("Failed to retrieve playlist information.")

                else:

                    playlists = json.loads(playlist_result.content)

                    # Get the playlists from the response
                    playlists_data = playlists['playlists']['items']

                    for playlist in playlists_data:
                        
                        # Getting only user made playlists
                        if playlist['owner']['id'] != 'spotify':
                            
                            user_playlists.append(playlist)
                            
                            # Checking if the number of playlists has not crossed 60
                            if len(user_playlists) >= 60:

                                break
                    
                    # Resetting parameters to accomodate offset number 
                    params = {
                        'type': 'playlist',
                        'limit': 50,
                        'offset': offset + len(playlists)
                    }

                    # Write the playlist links to a text file
                    with open('data/playlists/%s_playlists.txt' % genre, 'w') as f:
                        
                        for playlist in user_playlists:
                            
                            playlist_url = playlist['external_urls']['spotify']
                            f.write(playlist_url + '\n')

                    time.sleep(3)                            

if __name__ == "__main__":

    start_time = time.time()
    
    token = get_token()

    get_playlists(token)

    end_time = time.time()
    runtime = end_time - start_time
    print(f"Runtime: {runtime:.2f} seconds")
    print('Done!')
