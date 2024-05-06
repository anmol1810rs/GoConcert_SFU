"""
    This file contains the code for the Machine Learning Model 
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

#------------------------------------------------------- Imports and Reading Cleaned Spotify Data ------------------------------------------------------ 

#Importing the necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.stem import WordNetLemmatizer
from difflib import SequenceMatcher
nltk.download('omw-1.4')
nltk.download('wordnet')
import pickle

#Reading the final Spotify Data (cleaned)
spotify_df = pd.read_csv('data/csv/clean_data/clean_data.csv')
spotify_df = spotify_df.dropna(how='any')
spotify_df.head()

#--------------------------------------------------------- Natural Language Processing ------------------------------------------------------ 

#NLP Code - Lemmatization Technique
lemmatizer = WordNetLemmatizer()

#Define the Ticket Master Genre List
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

#Define a function to lemmatize words
def lemmatize_word(word):
    return lemmatizer.lemmatize(word, pos='n')

#Define a function that splits each genre and finds the closest lemma based on the Genre List provided.
def lemmatize_genre(genres_str):
    # split the string on ',' and remove any leading/trailing spaces
    genres_list = [genre.strip() for genre in genres_str.split(',')]
    # convert to lowercase and remove spaces
    genres_list = [genre.lower().replace(' ', '') for genre in genres_list]
    # find the closest match in the MGL
    closest_match = max(tkm, key=lambda x: sum([SequenceMatcher(None, genre, x).ratio() for genre in genres_list]))
    # lemmatize the closest match and return it
    return lemmatize_word(closest_match)


#---------------------------------------------------- Feature Engineering and Data Preprocessing ------------------------------------------------------ 

#Normalize the loudness feature to a 0-1 scale
def loudness_norm(loudness, min_l, max_l):
  #Applying the min max scaler formula
  l_min = min_l
  l_max = max_l
  return float((loudness - l_min)/(l_max - l_min))

#Normalizing the tempo  feature on a 0 to 1 scale
def tempo_norm(tempo, min_tempo, max_tempo):
  #Applying the min max scaler formula
  t_min = min_tempo
  t_max = max_tempo
  return float((tempo - t_min)/(t_max - t_min))

#Applying the Loudness Normalization function
max_loudness = spotify_df['loudness'].max()
min_loudness = spotify_df['loudness'].min()
spotify_df['loudness'] = spotify_df['loudness'].apply(lambda x: loudness_norm(x, min_loudness, max_loudness))

#Applying the Tempo Normalization function
max_temp = spotify_df['tempo'].max()
min_temp = spotify_df['tempo'].min()
spotify_df["tempo"] = spotify_df['tempo'].apply(lambda x: tempo_norm(x, min_temp, max_temp))

#Applying the NLP - Lemmatization for each genre
spotify_df['genre'] = spotify_df['artist_genre'].apply(lambda x: lemmatize_genre(x))

#Count the occurrences of each unique genre
genre_counts = spotify_df['genre'].value_counts()

#Print the genre counts
print(genre_counts)

#Making a features dataframe for easier access to only the required features
audio_features = ["acousticness", "danceability", "energy", "instrumentalness", "liveness", "key", "mode", "loudness", "speechiness", "tempo", "valence", "genre"]
features_df = spotify_df.loc[:, audio_features]

#Rounding the Numerical Features to the nearest 3 decimal places
numerical_audio_features = ["acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "tempo", "valence"]
for feature in numerical_audio_features:
  features_df[feature] = features_df[feature].round(3)

#--------------------------------------------------------- ML MODELING FOR CLASSIFICATION ------------------------------------------------------ 

#Label Encoding the genre feature for classification purposes
labelencoder = LabelEncoder()

#Making a Label Map to access the encoded categorical features during testing
y_le = features_df['genre']
features_df['genre'] = labelencoder.fit_transform(features_df['genre'])
label_map = dict(zip(y_le, features_df['genre']))
print(label_map)

#Selecting the Input and the Output Features before Classification
X = features_df[["acousticness", "danceability", "energy", "instrumentalness", "liveness", "key", "mode", "loudness", "speechiness", "tempo", "valence"]]
Y = features_df["genre"]

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=42)


#---------------------------------------------------------- ML PREDICTION AND TESTING ------------------------------------------------------ 

#Trying the Random Forest Model
from sklearn.ensemble import RandomForestClassifier
rfm = RandomForestClassifier(n_estimators = 10)
rfm.fit(X_train, y_train)

#Predicting the genre using the rfm model
y_pred = rfm.predict(X_test)

#Printing the Confusion Matrix for the predictions obtained using the rfm model
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test, y_pred))

#Making the .pkl file for the model and the label map for prediction on the Web App
with open('/content/drive/MyDrive/Spotify_BDP/RFmodel_36.pkl', 'wb') as files:
    pickle.dump(rfm, files)

with open('/content/drive/MyDrive/Spotify_BDP/label_map_36.pkl', 'wb') as files:
    pickle.dump(label_map, files)
