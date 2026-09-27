# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "altair",
#     "marimo",
#     "pandas",
# ]
# ///
"""src/datafun/movies_notebook.py - Reactive MovieLens SQL explorer.

Author: Shalynne Orth
Date: 2026-09

REQUIREMENTS:

1. Add marimo to notebooks in pyproject.toml.
2. Install the required dependencies using **uv sync**.

RUN:

Open this project folder in VS Code.
Open an integrated Terminal in the root project folder
and paste the following command.

uv run marimo run src/datafun/movies_notebook.py

EDIT:

uv run marimo edit src/datafun/movies_notebook.py

DOMAIN:

MovieLens movie ratings.

The data is stored in two related tables:
one table of movies and one table of user ratings.
A movie can have many ratings.

EXPLORE:

Use the slider to choose a minimum number of ratings.

Python passes the selected threshold to SQL as a bound parameter.
SQL joins the movies and ratings tables, calculates each movie's average
rating, and returns the ten highest-rated qualifying movies.

Python displays the query results in a table and interactive chart.

Change the minimum rating count and Marimo automatically updates the
results and chart.

NO LOGGING:

In this notebook, we do not configure logging because a browser-based
WASM app has no persistent Python server to store log files.

PLAN CELLS:

1. opening Markdown and analyst insight
2. load related MovieLens data
3. create database for SQL
4. choose a minimum rating count
5. run a parameterized SQL query
6. show the analytical choice
7. show the results table and chart

Note: No need to call @app.cell functions in marimo,
it triggers them automagically.
I could name them all "_", but I choose to
give them internal function names starting with "_"
so I can organize my thinking and my app.
"""

# === 0: DECLARE IMPORTS AND CREATE APP ===

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


with app.setup:
    from pathlib import Path
    import sqlite3
    import sys

    import altair as alt
    import marimo as mo
    import pandas as pd

    notebook_location = mo.notebook_location()
    if notebook_location is None:
        raise RuntimeError("Unable to determine notebook location.")

    NOTEBOOK_LOCATION = Path(notebook_location)

    DATA_DIR = NOTEBOOK_LOCATION.parents[1] / "data" / "movies"
    PUBLIC_DIR = NOTEBOOK_LOCATION / "public"

    MOVIES_FILENAME = "movies.csv"
    RATINGS_FILENAME = "ratings.csv"

    def load_csv_for_notebook(
        *,
        local_path: Path,
        public_path: Path,
    ) -> pd.DataFrame:
        """Load a CSV locally or in a deployed WASM app."""
        if sys.platform == "emscripten":
            from pyodide.http import open_url

            return pd.read_csv(open_url(str(public_path)))

        if not local_path.is_file():
            raise FileNotFoundError(f"Required data file not found: {local_path}")

        return pd.read_csv(local_path)


@app.cell
def _title():
    mo.md(r"""
    # MovieLens Rating Explorer

    Explore MovieLens data with SQL and Python.

    This app joins a movies table to a ratings table using `movieId`.
    Choose a minimum number of ratings to find highly rated movies with
    enough ratings to make the results more meaningful.

    ## Analyst Insight

    At a minimum of 50 ratings, several highly rated movies appeared in the
    top ten with fewer than 100 ratings. When the minimum increased to 100,
    those movies no longer qualified and were replaced by movies supported by
    more audience ratings.

    This shows that the rating-count threshold changes the evidence required
    for a movie to appear in the ranking. A higher threshold favors results
    based on a larger number of user ratings, although it does not prove that
    one movie is objectively better than another.

    ---
    """)


@app.cell
def _load_data():
    # === LOAD THE RELATED MOVIE DATA ===

    movies_df = load_csv_for_notebook(
        local_path=DATA_DIR / MOVIES_FILENAME,
        public_path=PUBLIC_DIR / MOVIES_FILENAME,
    )

    ratings_df = load_csv_for_notebook(
        local_path=DATA_DIR / RATINGS_FILENAME,
        public_path=PUBLIC_DIR / RATINGS_FILENAME,
    )

    return movies_df, ratings_df


@app.cell
def _create_database(movies_df, ratings_df):
    # === CREATE AN IN-MEMORY SQLITE DATABASE ===

    connection = sqlite3.connect(":memory:")

    movies_df.to_sql(
        "movies",
        connection,
        if_exists="replace",
        index=False,
    )

    ratings_df.to_sql(
        "ratings",
        connection,
        if_exists="replace",
        index=False,
    )

    mo.md("SQLite database connected and MovieLens tables loaded.")

    return (connection,)


@app.cell
def _choose_minimum_ratings():
    # === CHOOSE A MINIMUM NUMBER OF RATINGS ===

    minimum_ratings_slider = mo.ui.slider(
        start=10,
        stop=200,
        step=10,
        value=50,
        label="Minimum number of ratings",
    )

    minimum_ratings_slider

    return (minimum_ratings_slider,)


@app.cell
def _run_query(connection, minimum_ratings_slider):
    # === RUN A PARAMETERIZED SQL QUERY ===

    sql_query = """
    SELECT
        m.title,
        m.genres,
        COUNT(r.rating) AS rating_count,
        ROUND(AVG(r.rating), 2) AS average_rating
    FROM movies AS m
    JOIN ratings AS r
        ON m.movieId = r.movieId
    GROUP BY
        m.movieId,
        m.title,
        m.genres
    HAVING COUNT(r.rating) >= ?
    ORDER BY
        average_rating DESC,
        rating_count DESC,
        m.title ASC
    LIMIT 10;
    """

    result_df = pd.read_sql_query(
        sql_query,
        connection,
        params=[minimum_ratings_slider.value],
    )

    return result_df, sql_query


@app.cell
def _show_selection(minimum_ratings_slider):
    mo.md(
        f"""
        ## Top-Rated Movies

        Showing the ten highest-rated movies with at least
        **{minimum_ratings_slider.value} ratings**.
        """
    )


@app.cell
def _show_df_table_and_chart(minimum_ratings_slider, result_df):
    movie_chart = (
        alt.Chart(result_df)
        .mark_bar()
        .encode(  # ty: ignore[unresolved-attribute]
            x=alt.X(
                "average_rating:Q",
                title="Average User Rating",
                scale=alt.Scale(domain=[0, 5]),
            ),
            y=alt.Y("title:N", title="Movie", sort="-x"),
            tooltip=[
                alt.Tooltip("title:N", title="Movie"),
                alt.Tooltip("average_rating:Q", title="Average Rating"),
                alt.Tooltip("rating_count:Q", title="Number of Ratings"),
                alt.Tooltip("genres:N", title="Genres"),
            ],
        )
        .properties(
            title=(
                f"Top 10 Movies with at Least {minimum_ratings_slider.value} Ratings"
            ),
            width="container",
            height=350,
        )
    )

    mo.vstack(
        [
            result_df,
            movie_chart,
        ]
    )


if __name__ == "__main__":
    app.run()
