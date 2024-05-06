"""
    This file contains the code for the Machine Learning Model Evaluation (Version 1.0)
    that predicts the genre of a song based on the audio features of the song.

    - Input: 
        Audio Features of a song
    
    - Output: 
        Genre of the song

    The code is divided into the following sections:
    1. Imports and Reading Cleaned Spotify Data
    2. Natural Language Processing
    3. Feature Engineering and Data Preprocessing
    4. ML Modeling for Classification
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle

test_df = pd.read_csv('Test.csv')
test_df.head()

# Load the trained models from the pickle file
with open('rfmodel_36_final.pkl', 'rb') as file:
    rfm1 = pickle.load(file)

with open('rfmodel_60_final.pkl', 'rb') as file:
    rfm2 = pickle.load(file)
    
label_map1 = pickle.load(open('label_map_36_final.pkl', 'rb'))
label_map2 = pickle.load(open('label_map_60_final.pkl', 'rb'))

# Define a function to convert loudness values to a 0-1 scale
def loudness_norm(loudness, min_l, max_l):
  #Applying the min max scaler formula
  l_min = min_l
  l_max = max_l
  return float((loudness - l_min)/(l_max - l_min))

#Normalizing the tempo on a 0 to 1 scale
def tempo_norm(tempo, min_tempo, max_tempo):
  #Applying the min max scaler formula
  t_min = min_tempo
  t_max = max_tempo
  return float((tempo - t_min)/(t_max - t_min))

max_loudness = test_df['loudness'].max()
min_loudness = test_df['loudness'].min()
test_df['loudness'] = test_df['loudness'].apply(lambda x: loudness_norm(x, min_loudness, max_loudness))

max_temp = test_df['tempo'].max()
min_temp = test_df['tempo'].min()
test_df["tempo"] = test_df['tempo'].apply(lambda x: tempo_norm(x, min_temp, max_temp))

numerical_audio_features = ["acousticness", "danceability", "energy", "instrumentalness",
                            "liveness", "loudness", "speechiness", "tempo", "valence"]

for feature in numerical_audio_features:
  test_df[feature] = test_df[feature].round(3)

#Making a genre dictionary to store unique genres and their respective count
genres_dict={}

# Predictions using rfm36
for _, row in test_df.iterrows():
    # Extract the features from the row and Reshape to 2D array for compatibility with model
    features = row[["acousticness", "danceability", "energy", "instrumentalness",
                    "key", "mode", "liveness", "loudness", "speechiness", 
                    "tempo", "valence"]].values.reshape(1, -1)
    
    # Use the trained model to predict the output
    pred = rfm1.predict(features)[0]
    key = [k for k, v in label_map1.items() if v == pred]
    genre = key[0].lower()
    if(genre in genres_dict):
        genres_dict[genre]+=1
    else:
        genres_dict[genre]=1


# Predictions using rfm60
for _, row in test_df.iterrows():
    # Extract the features from the row and Reshape to 2D array for compatibility with model
    features = row[["acousticness", "danceability", "energy", "instrumentalness",
                    "key", "mode", "liveness", "loudness", "speechiness", 
                    "tempo", "valence"]].values.reshape(1, -1)
    
    # Use the trained model to predict the output
    pred = rfm2.predict(features)[0]
    key = [k for k, v in label_map2.items() if v == pred]
    genre = key[0].lower()
    if(genre in genres_dict):
        genres_dict[genre]+=1
    else:
        genres_dict[genre]=1

#Sorting a dicitonary based on the counts obained 
sorted_dict = dict(sorted(genres_dict.items(), key=lambda item: item[1], reverse=True))
print(sorted_dict)

# create a list of sorted keys
sorted_keys = list(sorted_dict.keys())

sorted_keys = sorted_keys[:5]
print(sorted_keys)
    