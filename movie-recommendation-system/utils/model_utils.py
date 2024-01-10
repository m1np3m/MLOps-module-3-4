import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import spmatrix
import os, sys


class Recommender:
    def __init__(self, df: pd.DataFrame, max_features: int) -> None:
        self.tfidf = TfidfVectorizer(max_features=max_features)
        self.df = df
        pass

    def map_movie_title_to_idx(self) -> pd.Series:
        self.movie2idx = pd.Series(self.df.index, index=self.df["title"])
        return self.movie2idx

    def init_matrix(self) -> spmatrix:
        self.matrix = self.tfidf.fit_transform(self.df["string"])
        return self.matrix

    # create a function that generates recommendations
    def recommend(self, title, k) -> pd.Series:
        if self.movie2idx == None:
            print("Run recommender.map_movie_title_to_idx() first")
            sys.exit(1)
        if self.matrix == None:
            print("Run recommender.init_matrix() first")
            sys.exit(1)

        # get the row in the dataframe for this movie
        idx = self.movie2idx[title]
        if type(idx) == pd.Series:
            idx = idx.iloc[0]

        # calculate the pairwise similarities for this movie
        query = self.matrix[idx]
        scores = cosine_similarity(query, self.matrix)

        # currently the array is 1 x N, make it just a 1-D array
        scores = scores.flatten()

        # get the indexes of the highest scoring movies
        # get the first K recommendations
        # don't return itself!
        recommended_idx = (-scores).argsort()[1 : k + 1]

        # return the titles of the recommendations
        return self.df["title"].iloc[recommended_idx]
