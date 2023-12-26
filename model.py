# Import the pandas library as pd
import pandas as pd 

# Load the movie dataset from a CSV file and select only the 'movieId' and 'title' columns
movie = pd.read_csv("movie.csv")
movie = movie.loc[:,["movieId","title"]]

# Load the rating dataset from a CSV file and select 'userId', 'movieId', and 'rating' columns
rating = pd.read_csv("rating.csv")
rating = rating.loc[:,["userId","movieId","rating"]]

# Merge the movie and rating datasets based on common columns
data = pd.merge(movie, rating)

# Truncate the data to the first 2,000,000 rows
data = data.iloc[:2000000,:]

# Create a pivot table where rows are users, columns are movie titles, and values are ratings
pivot_table = data.pivot_table(index = ["userId"], columns = ["title"], values = "rating")

# Define a function to find movies similar to a given movie
def movie(input):
    # Select the column corresponding to the input movie to find users who watched it
    movie_watched = pivot_table[input]

    # Calculate the correlation of the watched movie with other movies in the pivot table
    similarity_with_other_movies = pivot_table.corrwith(movie_watched)

    # Return the titles of the top 5 most similar movies
    return similarity_with_other_movies.head().index.tolist()
