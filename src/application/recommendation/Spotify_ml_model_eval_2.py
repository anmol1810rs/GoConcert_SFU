'''

This file contains the code for the evaluation of the trained model on the Spotify dataset.
The model is trained on the Spotify dataset and the trained model is saved in the pickle file.
The trained model is loaded from the pickle file and the model is evaluated on the Spotify dataset.

input: Spotify dataset filename

output: Genre of the playlist

usage: python spotify_ml_model_eval_2.py <filename>

'''

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle


def getGenre(filename):

  '''
  This function takes the filename of the Spotify dataset as input and returns the genre of the playlist.

  Args:
      param1 (str): filename of the Spotify dataset

  Returns:
      str: an array of top 5 recomended genres for playlist
  '''
    
  test_df = pd.read_csv(filename)
  test_df.head()

  print('-----------------------------------------------------------------------------------------------------------------------------')
  print('-----------------------------------------------------------------------------------------------------------------------------')


  # define the TicketMaster List
  tkm = [
      'alternative',
      'ballads',
      'romantics',
      'blues',
      'bollywood',
      'chanson francaise',
      'children',
      'classical',
      'country',
      'dance',
      'electronic',
      'folk',
      'hip-hop',
      'rap',
      'holiday',
      'jazz',
      'latin',
      'medieval/renaissance',
      'metal',
      'new age',
      'other',
      'pop',
      'r&b',
      'reggae',
      'religious',
      'rock',
      'world'
  ]
  # Load the trained models from the pickle file
  with open('recommendation/rfmodel_36_final.pkl', 'rb') as file:
      rfm1 = pickle.load(file)

  with open('recommendation/rfmodel_60_final.pkl', 'rb') as file:
      rfm2 = pickle.load(file)
      
  label_map1 = pickle.load(open('recommendation/label_map_36_final.pkl', 'rb'))
  label_map2 = pickle.load(open('recommendation/label_map_60_final.pkl', 'rb'))

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
  final_genres_dict={}

  # # Predictions using rfm36
  for _, row in test_df.iterrows():
      # Extract the features from the row and Reshape to 2D array for compatibility with model
      features = row[["acousticness", "danceability", "energy", "instrumentalness",
                      "key", "mode", "liveness", "loudness", "speechiness", 
                      "tempo", "valence"]].values.reshape(1, -1)
      
      # Use the trained model to predict the output
      prediction_36 = rfm1.predict(features)[0]
      prediction_60 = rfm2.predict(features)[0]

      key_36 = [k for k, v in label_map1.items() if v == prediction_36]
      key_60 = [k for k, v in label_map2.items() if v == prediction_60]

      key_36 = key_36[0].lower()
      key_60 = key_60[0].lower()

      print(key_36, key_60)

      genres_dict[key_36] = genres_dict.get(key_36, 0) + 4 # 40% weightage
      genres_dict[key_60] = genres_dict.get(key_60, 0) + 6 # 60% weightage

      print(genres_dict[key_36], genres_dict[key_60])

      # Use majority voting to produce the final prediction
      final_prediction = max(genres_dict[key_36], genres_dict[key_60] )
      print(final_prediction)
      
      genre = ""

      if(final_prediction == genres_dict[key_36]):
        genre = key_36
      else:
        genre = key_60

      print(genre)
      if(genre in final_genres_dict):
          final_genres_dict[genre]+=1
      else:
          final_genres_dict[genre]=1

  #Sorting a dicitonary based on the counts obained 
  sorted_dict = dict(sorted(final_genres_dict.items(), key=lambda item: item[1], reverse=True))
  print(sorted_dict)

  # create a list of sorted keys
  sorted_keys = list(sorted_dict.keys())

  new_sorted_keys = []
  l=0

  #Realigning the sorted_key with naming convention as per ticketmaster genres
  for i in range(0, len(sorted_keys)):
    for j in range(0, len(tkm)):
        if( (sorted_keys[i] in tkm[j]) or (tkm[j] in sorted_keys[i]) ):
          new_sorted_keys.append(tkm[j])
          l+=1

  new_sorted_keys = new_sorted_keys[:5]

  # return the top 5 predicted genres
  return new_sorted_keys
