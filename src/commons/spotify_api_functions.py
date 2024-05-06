"""
    This file contains extra helper functions used to get extra data from the Spotify's API.
    This file is currently not being used in the application and can be used to see what kind of data
    the API can retrieve.
"""

from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import time

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():

    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type":"application/x-www-form-urlencoded"
        }
    
    data = {"grant_type": "client_credentials"}

    result = post(url, headers = headers, data = data)

    json_result = json.loads(result.content)

    token = json_result["access_token"]
    return token


def get_auth_header(token):

    return {"Authorization":"Bearer " + token}


def api_request(url, headers, params=None, data=None):

    retry = True

    while retry:

        response = get(url, headers=headers, params=params, data=data)

        if response.status_code == 200:
            return response
        
        elif response.status_code == 429:

            retry_after = int(response.headers.get('Retry-After'))
            print(f"Rate limit exceeded. Wait for {retry_after} seconds before trying again.")
            return 'Try again'
        else:

            print(f"Request failed with error {response.status_code}: {response.text}")
            
            return None
        
def search_for_artist(token, artist_name):

    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    query = f"q={artist_name}&type=artist&limit=1"

    query_url = url + "?" + query

    result = get(query_url, headers = headers)

    artist_id = json.loads(result.content)["artists"]["items"][0]["id"]
    if len(artist_id) ==0:
        print("No artist found with this name")
        return None

    else:
        return artist_id

def search_for_track(token, track_name):

    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)

    query = f"q={track_name}&type=track&limit=1"

    query_url = url + "?" + query

    result = get(query_url, headers = headers)

    track_id = json.loads(result.content)["tracks"]["items"][0]["id"]
    if len(track_id) == 0:
        print("No track found with this name")
        return None

    else:
        return track_id

def get_top_songs_by_artists(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)

    result = get(url, headers = headers)

    json_result = json.loads(result.content)["tracks"]

    tracks_dict = {
        "tracks" : []
    }

    tracks_list = []
    for index, track in enumerate(json_result):

        if index == 10:
            break

        tracks = get_track_info(track)

        tracks_list.append(tracks)
    
    tracks_dict["tracks"] = tracks_list

    json_result_formatted = json.dumps(tracks_dict, indent=4)
    if len(json_result) ==0:
        print("No artist found with this name")
        return None

    else:
        return tracks_dict

def get_songs_by_playlists(token, playlist_id):

    playlist_info_url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    headers = get_auth_header(token)

    playlist_result = api_request(playlist_info_url, headers = headers)

    playlist_info_dict = {
        'name' : None,
        'owner display name' : None,
        'owner id' : None,
        'followers' : None,
        'tracks' : None
        }

    if playlist_result is None or playlist_result == 'Try again':

        print("Failed to retrieve playlist information.")

    else:

        playlist_info = json.loads(playlist_result.content)

        playlist_info_dict['name'] = playlist_info["name"]
        playlist_info_dict['owner display name'] = playlist_info["owner"]["display_name"]
        playlist_info_dict['owner id'] = playlist_info["owner"]["id"]
        playlist_info_dict['followers'] = playlist_info["followers"]["total"]

    # Creating offset to parse all tracks
    offset = 0
    track_ids = []

    while True:

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit=100"
        headers = get_auth_header(token)

        result = api_request(url, headers = headers)

        if playlist_result is None or playlist_result == 'Try again':

            print("Failed to retrieve playlist information.")

        else:

            playlist= json.loads(result.content)

            playlist_tracks = playlist["items"]
            for item in playlist_tracks:
                track_id = item['track']['id']
                track_ids.append(track_id)

            if playlist['next']:

                offset += 100
            else:

                break
            
    playlist_info_dict['tracks'] = track_ids
    
    return playlist_info_dict

def get_artist(token, artist_id):

    url = f"https://api.spotify.com/v1/artists/{artist_id}"

    headers = get_auth_header(token)

    result = get(url, headers = headers)

    if result.status_code == 429:
        retry_after = int(result.headers.get('Retry-After'))
        print(f"Rate limit exceeded. Wait for {retry_after} seconds before trying again.")
        return 'try again'
    
    elif result.status_code == 200:

        json_result = json.loads(result.content)

        followers = json_result["followers"]["total"]
        artist_genre = json_result["genres"]
        artist_name = json_result["name"]
        artist_popularity = json_result["popularity"]

        artist_metadata = {
            "followers" : followers,
            "genres" : artist_genre, 
            "name" : artist_name,
            "id" : artist_id,
            "popularity" : artist_popularity
        }
        if len(result.content) ==0:
            print("Wrong ID")
            return None

        else:
            return artist_metadata

def get_track_info(track):

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

    tracks["id"] = track["id"]
    tracks["name"]= track["name"]
    # tracks["artist id"] = track["album"]["artists"][0]["id"]
    tracks["popularity"] = track["popularity"]
    tracks["duration_ms"] = track["duration_ms"]
    tracks["album type"] = track["album"]["album_type"]
    tracks["album id"] = track["album"]["id"]
    tracks["album name"] = track["album"]["name"]
    tracks["album release date"] = track["album"]["release_date"]

    artists = track["artists"]

    artist_dict = {
        "name" : None,
        "id" : None
    }
    # genre = get_artist(token, artist_id)

    artist_name_list = []
    artist_id_list = []

    artist_dict_list = []         
    for artist in artists:

        artist_name_list.append(artist["name"])
        artist_id_list.append(artist["id"])
        
        artist_dict_list.append(artist_dict)
        
        artist_dict = {
            "name" : None,
            "id" : None
        }
    
    artist_id = artists[0]["id"]
    genre = get_artist(token, artist_id)["genres"]
    

    tracks["artist id"] = artist_id_list
    tracks["artists"] = artist_name_list
    tracks["artist genre"] = genre

    return tracks
    
def get_track_feature_info(track_features):

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


def get_track(token, track_id):

    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)

    result = get(url, headers = headers)

    track = json.loads(result.content)

    tracks = get_track_info(track)

    if len(tracks) ==0:
        print("No track found with this name")
        return None

    else:
        return tracks

def get_track_features(token, track_id):

    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = get_auth_header(token)

    result = get(url, headers = headers)

    features = json.loads(result.content)

    if len(features) ==0:
        print("No track found with this id")
        return None

    else:
        return get_track_feature_info(features)

def get_mul_tracks(token, playlist_id, track_id_list):

    params = {
        'ids' : ','.join(track_id_list[:50]), # Get first 50 tracks
        'market' : 'US'
    }

    playlist_track_info_dict = {
        'playlist id' : playlist_id,
        'tracks' : []
    }

    tracks_list = []

    url = f"https://api.spotify.com/v1/tracks"
    headers = get_auth_header(token)

    playlist_result = api_request(url, headers=headers, params=params)

    if playlist_result is None or playlist_result == 'Try again':

        print("Failed to retrieve playlist information.")

    else:
        
        tracks = json.loads(playlist_result.content)

        track_data = tracks['tracks']

        track_id_length = len(track_id_list)

        for track in track_data:
            
            track_info = get_track_info(track)

            tracks_list.append(track_info)
        
        offset = 50
        
        while offset < track_id_length:

            params['ids'] = ','.join(track_id_list[offset:offset+50])

            playlist_result = api_request(url, headers=headers, params=params)

            if playlist_result is None or playlist_result == 'Try again':

                print("Failed to retrieve playlist information.")

            else:   
                
                tracks = json.loads(playlist_result.content)

                track_data = tracks['tracks']

                for track in track_data:
                    
                    track_info = get_track_info(track)

                    tracks_list.append(track_info)
            
            offset += 50

    playlist_track_info_dict['playlist id'] = playlist_id
    playlist_track_info_dict['tracks'] = tracks_list

    return playlist_track_info_dict


def get_mul_tracks_features(token, playlist_id, track_id_list):

    params = {
        'ids' : ','.join(track_id_list[:100]), # Get first 100 tracks
    }

    playlist_track_feature_info_dict = {
        'playlist id' : playlist_id,
        'tracks' : []
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
            
            track_info = get_track_feature_info(track)

            tracks_features_list.append(track_info)
        
        offset = 100
        
        while offset < track_id_length:

            params['ids'] = ','.join(track_id_list[offset:offset+100])

            playlist_result = api_request(url, headers=headers, params=params)

            if playlist_result is None or playlist_result == 'Try again':

                print("Failed to retrieve playlist information.")

            else:   
                
                tracks = json.loads(playlist_result.content)

                track_data = tracks['audio_features']

                for track in track_data:
                    
                    track_info = get_track_feature_info(track)

                    tracks_features_list.append(track_info)
            
            offset += 100

    playlist_track_feature_info_dict['playlist id'] = playlist_id
    playlist_track_feature_info_dict['tracks'] = tracks_features_list

    return playlist_track_feature_info_dict

def concatenate_playlist_info(playlist_track_info, playlist_features_info):

    playlist_tracks_all_info_dict = {
        "playlist id" : None,
        "tracks" : []
        }
    
    track_info_id = playlist_track_info["playlist id"]
    track_features_id = playlist_tracks_features_info["playlist id"]

    playlist_tracks_list = playlist_track_info["tracks"]
    playlist_tracks_features_list = playlist_features_info["tracks"]

    if (track_info_id == track_features_id) and len(playlist_tracks_features_list) == len(playlist_tracks_list):

        playlist_tracks_all_info_dict["playlist id"] = track_info_id

        playlist_tracks_list = playlist_track_info["tracks"]
        playlist_tracks_features_list = playlist_features_info["tracks"]

        playlist_tracks_all_info_dict["tracks"] = [{**playlist_tracks_list[i], **playlist_tracks_features_list [i]}\
                                               for i in range(len(playlist_tracks_list))]

    return playlist_tracks_all_info_dict

def get_categories_playlists(token, category_id):

    offset = 0

    headers = get_auth_header(token)

    url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists"
    
    playlist_result = api_request(url, headers=headers, params={"limit": 1, "offset": 0})

    if playlist_result is None or playlist_result == 'Try again':

        print("Failed to retrieve playlist information.")
        

    else:

        total = json.loads(playlist_result.content)["playlists"]["total"]
        print("total: " , total)


    playlist_id_list = []

    while len(playlist_id_list) < total:
        
        params = {
            "limit" : 50,
            "country" : "US",
            "offset" : offset
        }
        url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists"
        headers = get_auth_header(token)
        
        playlist_result = api_request(url, headers=headers, params=params)

        if playlist_result is None or playlist_result == 'Try again':

            print("Failed to retrieve playlist information.")

        else:

            response = json.loads(playlist_result.content)

            
            playlist_list = response["playlists"]["items"]

            for playlists in playlist_list:

                if playlists == None:
                    total -= 1
                
                elif playlists != None:

                    playlist_id_list.append(playlists["id"])

            offset += 50

        #print(len((playlist_id_list)))

            

    print(len(list(set(playlist_id_list))))
    return response
    
if __name__ == "__main__":
    token = get_token()

    # Get Artist ID
    # artist_id = search_for_artist(token, "Goo Goo Dolls")
    # print(artist_id)
    # print("<-------------------------------------------------------->")

    # # Get Artist Info 
    # artist_info = get_artist(token, artist_id)
    # print(artist_info['genres'])
   
    # with open('artist_info.json', 'w', encoding='utf-8') as f:
    #     json.dump(artist_info, f, ensure_ascii=False, indent=4)

    # # Get an Artist's top 10 tracks
    # artist_top_tracks = get_top_songs_by_artists(token, artist_id)

    # with open('artist_top_tracks.json', 'w', encoding='utf-8') as f:
    #     json.dump(artist_top_tracks, f, ensure_ascii=False, indent=4)

    # # Search track ID
    # track_id = search_for_track(token, "Iris" )
    # print(track_id)

    # # Get a track info
    # track_info = get_track(token, "0G21yYKMZoHa30cYVi1iA8")
    # print(track_info)
    # with open('track_info.json', 'w', encoding='utf-8') as f:
    #     json.dump(track_info, f, ensure_ascii=False, indent=4)
    
    

    # # Get track features
    # track_features = get_track_features(token, track_id)
    # with open('track_features.json', 'w', encoding='utf-8') as f:
    #     json.dump(track_features, f, ensure_ascii= False, indent = 4)
    
    # Get playlists

    # playlist_id = "4u9fWaMH2qe5naVt1yYhI8"
    # playlists = get_songs_by_playlists(token, playlist_id)
    # with open('playlists.json', 'w', encoding='utf-8') as f:
    #     json.dump(playlists, f, ensure_ascii=False, indent=4)

    # playlist_tracks = playlists['tracks']
    # print(len(playlist_tracks))

    # playlist_tracks_info = get_mul_tracks(token, playlist_id, playlist_tracks)
    # with open('playlists_track_info.json', 'w', encoding='utf-8') as f:
    #     json.dump(playlist_tracks_info, f, ensure_ascii=False, indent=4)


    # playlist_tracks_features_info = get_mul_tracks_features(token, playlist_id, playlist_tracks)
    # with open('playlists_track_features_info.json', 'w', encoding='utf-8') as f:
    #     json.dump(playlist_tracks_features_info, f, ensure_ascii=False, indent=4) 
    

    # playlist_tracks_all_info = concatenate_playlist_info(playlist_tracks_info, playlist_tracks_features_info)
    # with open('playlists_track_all_info.json', 'w', encoding='utf-8') as f:
    #     json.dump(playlist_tracks_all_info, f, ensure_ascii=False, indent=4)
        
    # print('<------------------------------------------------------------------>')

    # category = 'rock'
    # category_playlist = get_categories_playlists(token, category)
    # with open(category + '_playlists.json', 'w', encoding='utf-8') as f:
    #     json.dump(category_playlist, f, ensure_ascii=False, indent=4)
       
    # songs = get_songs_by_artists(token, artist_id)

    # playlists = get_songs_by_playlists(token, "4tSeE8R6PnWYAKbwUGEblw")
    # track = get_tracks(token, "21jGcNKet2qwijlDFuPiPb")

    # with open('playlists.json', 'w', encoding='utf-8') as f:
    #     json.dump(playlists, f, ensure_ascii=False, indent=4)

    # with open('track.json', 'w', encoding='utf-8') as f:
    #     json.dump(track, f, ensure_ascii=False, indent=4)
    