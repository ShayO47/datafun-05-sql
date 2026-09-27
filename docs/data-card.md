# Data Card: MovieLens Rating Explorer

## Dataset Source

This project uses the
[MovieLens Latest Small Dataset](https://grouplens.org/datasets/movielens/latest/)
from GroupLens Research.

The dataset contains movie information and user rating activity. It is used here
for educational data analysis.

## Purpose

The purpose of this project is to identify highly rated movies while considering
how many user ratings support each result.

A movie with a high average rating from only a few users may be less reliable
than a similarly rated movie supported by many users. The interactive app lets
the user choose a minimum rating-count threshold before viewing results.

## Records and Grain

The project uses two related tables:

- `movies.csv`: one row represents one movie.
- `ratings.csv`: one row represents one user's rating of one movie.

The tables are connected with the `movieId` column.

## Variables Used

### movies.csv

| Variable | Description |
| --- | --- |
| `movieId` | Unique identifier for each movie |
| `title` | Movie title and release year |
| `genres` | One or more genres assigned to the movie |

### ratings.csv

| Variable | Description |
| --- | --- |
| `userId` | Identifier for the user who submitted a rating |
| `movieId` | Identifier connecting the rating to a movie |
| `rating` | User's rating of the movie |
| `timestamp` | Time the rating was recorded |

## Processing and Analysis

The Marimo app loads both CSV files into an in-memory SQLite database.

SQL joins the `movies` and `ratings` tables using `movieId`. The query then:

1. counts the ratings for each movie;
2. calculates each movie's average rating;
3. filters movies using the selected minimum rating count;
4. sorts the results by average rating;
5. returns the top ten qualifying movies.

## Results

With a minimum of 50 ratings, *The Shawshank Redemption (1994)* had the
highest average rating: 4.43 out of 5 from 317 ratings.

Increasing the threshold to 100 ratings removed movies with fewer than 100
ratings from the ranking and replaced them with movies supported by more user
feedback.

## Limitations

- The dataset represents MovieLens user activity, not all movie viewers.
- User IDs do not provide demographic information about the people who rated
  the movies.
- Average ratings are opinions from MovieLens users, not objective measures of
  movie quality.
- A higher minimum rating count provides more supporting evidence, but it may
  exclude highly rated movies with fewer ratings.
