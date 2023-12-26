# Import necessary libraries
import numpy as np
import pandas as pd
from tensorflow import keras
import tensorflow as tf
from keras.utils import plot_model
from sklearn.model_selection import train_test_split

# Load the rating dataset and limit to the first 200,000 rows
df = pd.read_csv('rating.csv')
df = df.iloc[:300000,:]

# Prepare the feature (X) and target (y) variables
X = df[['userId', 'movieId']]
y = df['rating']

# Split the dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create lists of unique users and movies
users = df.userId.unique().tolist()
movies = df.movieId.unique().tolist()

# Load the movie dataset
movies_df = pd.read_csv('movie.csv')

# Create dictionaries for encoding and decoding movie and user IDs
movie2movie_encoded = {x: i for i, x in enumerate(movies)}
movie_encoded2movie = {i: x for i, x in enumerate(movies)}
user2user_encoded = {x: i for i, x in enumerate(users)}
user_encoded2user = {i: x for i, x in enumerate(users)}

# Function to load the trained model
def load_model():
    model = keras.models.load_model('model.h5')
    return model

# Function to get the top k ratings
def get_top_ratings(ratings, k=10):
    top_ratings = ratings.argsort()[-k-1:]
    top_ratings = [movie_encoded2movie.get([x][0]) for x in top_ratings]
    return top_ratings

# Function to predict top movie recommendations for a given user
def predict(user_id):
    user_id = np.uint64(user_id)

    # Validation to ensure user ID is within range
    if user_id > len(df.userId.unique().tolist()):
        return 1

    # Identify movies watched by the user and movies not watched
    watched_movs = df[df.userId == user_id].iloc[:,1]
    not_watched_movs = movies_df[~movies_df.movieId.isin(watched_movs.values)].movieId

    # Filter and encode the not-watched movies
    not_watched_movs = list(set(not_watched_movs).intersection(set(movie2movie_encoded.keys())))
    not_watched_movs = [[movie2movie_encoded.get(x)] for x in not_watched_movs]

    # Encode the user ID and prepare the input array for the model
    user_encoder = user2user_encoded.get(user_id)
    user_movie_array = np.hstack(([[user_encoder]] * len(not_watched_movs), not_watched_movs))

    # Load the model and predict ratings
    model = load_model()
    ratings = model.predict([user_movie_array[:,0], user_movie_array[:,1]]).flatten()

    # Get the top 5 rated movies
    top_ratings = get_top_ratings(ratings, 5)

    # Fetch the movie titles for the top-rated movies
    top_movies = movies_df[movies_df.movieId.isin(top_ratings)]
    movie_titles = [element.title for element in top_movies.itertuples()]

    return movie_titles

# Function to get the top watched movies for a given user
def get_top_watched_movies(user_id):
    user_id = np.uint64(user_id)
    movies_df = pd.read_csv('movie.csv')

    # Select the top 5 movies based on rating for the user
    top_watched_movies = df[df.userId == user_id].sort_values(by='rating', ascending=False).movieId.head(5)
    top_watched_movies = movies_df[movies_df.movieId.isin(top_watched_movies.values)]

    # Compile a list of titles for these top watched movies
    watched_movie_titles = [element.title for element in top_watched_movies.itertuples()]
    
    return watched_movie_titles
