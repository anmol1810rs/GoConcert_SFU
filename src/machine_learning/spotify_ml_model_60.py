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

# Importing the necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.stem import WordNetLemmatizer
from difflib import SequenceMatcher
nltk.download('omw-1.4')
nltk.download('wordnet')
import pickle

#Reading the ifnal Spotify Data (cleaned)
spotify_df = pd.read_csv('data/csv/clean_data/clean_data.csv')
spotify_df = spotify_df.dropna(how='any')

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

#Defining a function that performs Bag of Words to find the genres and track their count
def make_word_dict(s):
    """
    This function takes a string and breaks each word at special characters and extracts all words from the list
    to make a dictionary of all the existing words.
    """
    word_dict = {}
    special_chars = [', ', ',']
    for char in special_chars:
        s = s.replace(char, ' ')
    words = s.split()
    for word in words:
        if word not in word_dict:
            word_dict[word] = 1
        else:
            word_dict[word] += 1
    return word_dict

#Define a function that finds the Maximum occuring word from the genres list and checks their ecistence on the Ticketmaster Platform
def find_max_word(s, word_dict):
    """
    This function takes a string and a word dictionary as input and returns the word in the string with the maximum count
    in the dictionary.
    """
    special_chars = [', ', ',']
    for char in special_chars:
        s = s.replace(char, ' ')
    words = s.split()
    max_word = None
    max_count = 0
    for word in words:
        if word not in tkm:
          max_word = 'other'
          max_count = 0
        elif word in word_dict and word_dict[word] > max_count:
            max_word = word
            max_count = word_dict[word]
    return max_word

#Making a Bag of Words for all the genres in the dataset
s = ''
word_dict = make_word_dict(s)
word_dict['other']=1

# Apply the two functions on each column value of the 'artist_genre' column in the spotify_df dataframe
for i, row in spotify_df.iterrows():
    # Apply Function 1 to extract words from the current column value and add them to the word_dict
    word_dict = {**word_dict, **make_word_dict(row['artist_genre'])}
    # Apply Function 2 to assign a single word to the current column value based on the maximum count in the word_dict
    max_word = find_max_word(row['artist_genre'], word_dict)
    spotify_df.at[i, 'artist_genre'] = max_word

#---------------------------------------------------- Feature Engineering and Data Preprocessing ------------------------------------------------------ 

#Define a function to normalize the loudness feature to a 0-1 scale
def loudness_norm(loudness, min_l, max_l):
  #Applying the min max scaler formula
  l_min = min_l
  l_max = max_l
  return float((loudness - l_min)/(l_max - l_min))

#Deinfe a fucntion to normalize the tempo feature to a 0 to 1 scale
def tempo_norm(tempo, min_tempo, max_tempo):
  #Applying the min max scaler formula
  t_min = min_tempo
  t_max = max_tempo
  return float((tempo - t_min)/(t_max - t_min))

#Applying the function to normalize loudness
max_loudness = spotify_df['loudness'].max()
min_loudness = spotify_df['loudness'].min()
spotify_df['loudness'] = spotify_df['loudness'].apply(lambda x: loudness_norm(x, min_loudness, max_loudness))

#Applying the function to normalize tempo
max_temp = spotify_df['tempo'].max()
min_temp = spotify_df['tempo'].min()
spotify_df["tempo"] = spotify_df['tempo'].apply(lambda x: tempo_norm(x, min_temp, max_temp))

#Finding counts of all the genres Obtained using the Bag of Words technique
counts = spotify_df['artist_genre'].value_counts()
print(counts)

#Removing the genre 'other' because it contains all the random genres that ight skew the predictions
spotify_df = spotify_df[spotify_df['artist_genre'] != 'other']
spotify_df['genre'] = spotify_df['artist_genre']

#--------------------------------------------------------- ML MODELING FOR CLASSIFICATION ------------------------------------------------------ 

#Label Encoding the genre feature for classification purposes
from sklearn.preprocessing import LabelEncoder
labelencoder = LabelEncoder()

#Making a Label Map to access the encoded categorical features during testing
y_le = spotify_df['genre']
spotify_df['genre'] = labelencoder.fit_transform(spotify_df['genre'])
label_map = dict(zip(y_le, spotify_df['genre']))
print(label_map)

#Selecting the Input and the Output Features before Classification
X = spotify_df[["acousticness", "danceability", "energy", "instrumentalness", "mode", "key", "liveness", "loudness", "speechiness", "tempo", "valence"]]
Y = spotify_df["genre"]

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.20, random_state=42)

#---------------------------------------------------------- ML PREDICTION AND TESTING ------------------------------------------------------ 

#Trying the KNN Model
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier(n_neighbors=100)
knn.fit(X_train, y_train)
#Predicting the genre using the knn model
y_pred = knn.predict(X_test)
#Printing the Confusion Matrix for the predictions obtained using the knn model
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test, y_pred))


#Trying the Random Forest Model
from sklearn.ensemble import RandomForestClassifier
rfm = RandomForestClassifier(n_estimators = 20)
rfm.fit(X_train, y_train)
#Predicting the genre using the rfm model
y_pred = rfm.predict(X_test)
#Printing the Confusion Matrix for the predictions obtained using the rfm model
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test, y_pred))


#Trying the XGBoost model
import xgboost as xgb
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
# Create the XGBoost classifier
xgb_classifier = xgb.XGBClassifier()
# Train the classifier
xgb_classifier.fit(X_train, y_train)
# Make predictions on the testing set
y_pred = xgb_classifier.predict(X_test)
# Generate the classification report
report = classification_report(y_test, y_pred)
print('Classification Report:')
print(report)
# Evaluate the classifier's accuracy
accuracy = accuracy_score(y_test, y_pred)
print('Accuracy:', accuracy)


#Trying the Naive Bayes Model
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
# Create the Naive Bayes classifier
nb_classifier = GaussianNB()
# Train the classifier
nb_classifier.fit(X_train, y_train)
# Make predictions on the testing set
y_pred = nb_classifier.predict(X_test)
# Generate the classification report
report = classification_report(y_test, y_pred)
print('Classification Report:')
print(report)
# Evaluate the classifier's accuracy
accuracy = accuracy_score(y_test, y_pred)
print('Accuracy:', accuracy)


#Making the .pkl file for the model and the label map for prediction on the Web App
with open('/content/drive/MyDrive/Spotify_BDP/rfmodel_60.pkl', 'wb') as f:
    pickle.dump(rfm, f)

with open('/content/drive/MyDrive/Spotify_BDP/label_map_60.pkl', 'wb') as f:
  pickle.dump(label_map, f)
