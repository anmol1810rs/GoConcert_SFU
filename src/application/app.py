from flask import Flask, request, redirect, url_for, render_template
import requests
from urllib.parse import quote, unquote
import sys
from pathlib import Path
from feature_engineering import test_playlist_to_csv
from analysis import playlist_analysis
from recommendation import spotify_ml_model_eval_2
import json
from concerts import concert_extraction


sys.path.insert(0, str(Path(__file__).parent.parent))

# create the flask app
app = Flask(__name__)

# application route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():

    # if the user has submitted the form i.e pressed the any button
    if request.method == 'POST':

                # if the user has pressed the analyse button
                if request.form['action'] == 'analyse':
                    
                    # get the user input playlist and extract the details in a csv file
                    user_text = request.form['text']
                    filename, status = test_playlist_to_csv.playlist_to_csv(user_text)

                    # if the user has entered an invalid playlist link
                    if status == 400:
                            
                                # redirect to the error page
                                return redirect(url_for('error'))

                    # analyse the csv file and return the features as well create the graphs
                    features = playlist_analysis.create_graphs(filename)

                    # serialize the feature array as a string
                    feature_str = json.dumps(features)

                    # encode the string as a URL parameter 
                    feature_encoded = quote(feature_str) 

                    # redirect to the analyse page and pass the features as a URL parameter
                    return redirect(url_for('analyse', features=feature_encoded))

                # if the user has pressed the recomend button
                elif request.form['action'] == 'recomend':

                    # get the user input playlist and extract the details in a csv file
                    user_text = request.form['text']
                    filename, status = test_playlist_to_csv.playlist_to_csv(user_text)

                    # if the user has entered an invalid playlist link
                    if status == 400:

                            # redirect to the error page
                            return redirect(url_for('error'))

                    # get the predicted genre of the user
                    user_genre = spotify_ml_model_eval_2.getGenre(filename=filename)

                    # serialize the array as a string
                    user_genre_str = json.dumps(user_genre) 

                    # encode the string as a URL parameter
                    user_genre_encoded = quote(user_genre_str)

                    # redirect to the recomend page and pass the user genre as a URL parameter
                    return redirect(url_for('recomend', user_genre=user_genre_encoded))

                # if the user has pressed the home button
                elif request.form['action'] == 'home':

                    # redirect to the home page
                    return redirect(url_for('index'))
                
                # if the user has pressed the about button
                elif request.form['action'] == 'about':

                    # redirect to the about page
                    return redirect(url_for('about'))
                
                # if the user has pressed the contact button
                elif request.form['action'] == 'contact':

                    # redirect to the contact page
                    return redirect(url_for('info'))

    # show the template for the home page          
    return render_template('index.html')


# application route for the analyse page
@app.route('/analyse', methods=['GET', 'POST'])
def analyse():

    # if the user has pressed a button
    if request.method == 'POST':

        # if the user has pressed the home button
        if request.form['action'] == 'home':
            
            # redirect to the home page
            return redirect(url_for('index'))
        # if the user has pressed the about button
        elif request.form['action'] == 'about':

            # redirect to the about page
            return redirect(url_for('about'))
                
        # if the user has pressed the contact button
        elif request.form['action'] == 'contact':

            # redirect to the contact page
            return redirect(url_for('info'))

    # get the features from the URL parameter
    feature_encoded = request.args.get('features')

    # decode the URL parameter
    feature_str = unquote(feature_encoded)

    # deserialize the string into an array
    feature = json.loads(feature_str)

    # create a dictionary to store the features
    feature_dict = {}
    feature_dict['total_songs'] = feature[0]
    feature_dict['avg_popularity'] = feature[1]
    feature_dict['most_listened_year'] = feature[2]
    feature_dict['most_listened_decade'] = feature[3]
    feature_dict['most_popular_track'] = feature[4]
    feature_dict['total_playlist_duration'] = feature[5]
    feature_dict['avg_track_duration'] = feature[6]
    feature_dict['uniqueness'] = feature[7]
    
    # display the analysis of the playlist
    return render_template('analyse.html', features=feature_dict)


# application route for the recomend page
@app.route('/recomend', methods=['GET', 'POST'])
def recomend():

    # get the user genre from the URL parameter
    user_genre_encoded = request.args.get('user_genre')

    # decode the URL parameter
    user_genre_str = unquote(user_genre_encoded)

    # deserialize the string into an array
    user_genre = json.loads(user_genre_str)

    # if the user has pressed a button
    if request.method == 'POST':

        # if the user has pressed the show recomendations button
        if request.form['action'] == 'showRecomendations':

            # get the city user input
            city = request.form.get('text')

            # get the start and end date user input
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            start_date = start_date
            end_date = end_date


            # generate the recommended events from ticketmaster
            genre_str = ', '.join(user_genre)
            concert_extraction.get_events(city, start_date, end_date, genre_str)

            # redirect to the show recomendations page
            return redirect(url_for('showRecomendations'))
        
        # if the user has pressed the home button
        elif request.form['action'] == 'home':

            # redirect to the home page
            return redirect(url_for('index'))

        # if the user has pressed the about button
        elif request.form['action'] == 'about':

            # redirect to the about page
            return redirect(url_for('about'))
                
        # if the user has pressed the contact button
        elif request.form['action'] == 'contact':

            # redirect to the contact page
            return redirect(url_for('info'))
    
    # display the recomendations page
    return render_template('recomend.html', genres=user_genre)

# application route for the show recomendations page
@app.route('/showRecomendations' , methods=['GET', 'POST'])
def showRecomendations():

    # if the user has pressed a button
    if request.method == 'POST':

        # if the user has pressed the home button
        if request.form['action'] == 'home':

            # redirect to the home page
            return redirect(url_for('index'))
            # if the user has pressed the about button
        elif request.form['action'] == 'about':

            # redirect to the about page
            return redirect(url_for('about'))
                
        # if the user has pressed the contact button
        elif request.form['action'] == 'contact':

            # redirect to the contact page
            return redirect(url_for('info'))

    # extract the events from the json file
    with open('data/events_scraped.json', 'r') as f:
        data = json.load(f)
    events = data['events']

    check = 0
    if len(events) == 0:
        check = 1
    
    # display the concert recomendations page
    return render_template('showRecomendations.html' , events=events, check=check)

# application route for the info page
@app.route('/info' , methods=['GET', 'POST'])
def info():
    
        # if the user has pressed a button
        if request.method == 'POST':
    
            # if the user has pressed the home button
            if request.form['action'] == 'home':
    
                # redirect to the home page
                return redirect(url_for('index'))
            
            # if the user has pressed the about button
            elif request.form['action'] == 'about':

                # redirect to the about page
                return redirect(url_for('about'))
            
            # if the user has pressed the contact button
            elif request.form['action'] == 'contact':
                    
                    # redirect to the contact page
                    return redirect(url_for('info'))
    
        # display the info page
        return render_template('info.html')

# application route for the info page
@app.route('/about' , methods=['GET', 'POST'])
def about():
    
        # if the user has pressed a button
        if request.method == 'POST':
    
            # if the user has pressed the home button
            if request.form['action'] == 'home':
    
                # redirect to the home page
                return redirect(url_for('index'))
            
            # if the user has pressed the about button
            elif request.form['action'] == 'about':

                # redirect to the about page
                return redirect(url_for('about'))
            
            # if the user has pressed the contact button
            elif request.form['action'] == 'contact':
                    
                    # redirect to the contact page
                    return redirect(url_for('info'))
    
        # display the info page
        return render_template('about.html')

# application route for the error page
@app.route('/error' , methods=['GET', 'POST'])
def error():
    
        # if the user has pressed a button
        if request.method == 'POST':
    
            # if the user has pressed the home button
            if request.form['action'] == 'home':
    
                # redirect to the home page
                return redirect(url_for('index'))
            
            # if the user has pressed the about button
            elif request.form['action'] == 'about':

                # redirect to the about page
                return redirect(url_for('about'))
            
            # if the user has pressed the contact button
            elif request.form['action'] == 'contact':
                    
                    # redirect to the contact page
                    return redirect(url_for('info'))
    
        # display the info page
        return render_template('error.html')

# run the flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    #app.run(debug=True)
