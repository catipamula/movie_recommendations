import streamlit as st
import pickle
import pandas as pd
import requests


# CONFIGURATION

API_KEY = "a6380491cc65873c1435ca0b246b02e9"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER_IMAGE = "https://via.placeholder.com/500x750?text=No+Image"
MOVIES_PER_PAGE = 10
MOVIES_PER_ROW = 5


# API FUNCTIONS

def fetch_poster_by_title(title):
    """Fetch poster image URL from TMDB API using movie title."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}"
    try:
        data = requests.get(url).json()
        if data.get("results"):
            poster_path = data["results"][0].get("poster_path")
            return f"{POSTER_BASE_URL}{poster_path}" if poster_path else PLACEHOLDER_IMAGE
        return PLACEHOLDER_IMAGE
    except Exception:
        return PLACEHOLDER_IMAGE


# RECOMMENDATION LOGIC

def recommend(movie):
    """Return recommended movie titles and poster URLs, including the searched movie."""
    movie_index = movies[movies[title_col] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        enumerate(distances),
        reverse=True,
        key=lambda x: x[1]
    )[:51]

    names, posters = [], []

    # Add searched movie first
    names.append(movies.iloc[movie_index][title_col])
    posters.append(fetch_poster_by_title(movies.iloc[movie_index][title_col]))

    # Add recommended movies
    for idx, _ in movies_list:
        if idx != movie_index:
            names.append(movies.iloc[idx][title_col])
            posters.append(fetch_poster_by_title(movies.iloc[idx][title_col]))
    return names, posters


# LOAD DATA

movies_dict = pickle.load(open("movies.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# Detect correct column names
title_col = "title" if "title" in movies.columns else movies.columns[0]


# PAGE CONFIG

st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")


# HEADER

st.markdown("<h1 style='text-align: center; color: white;'>🎥 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Find your next favorite movie!</p>", unsafe_allow_html=True)


# MOVIE SELECTION BAR

col1, col2 = st.columns([6, 1])
with col1:
    selected_movie_name = st.selectbox(
        "Choose a movie",
        movies[title_col].values,
        label_visibility="collapsed"
    )
    # Show poster preview immediately when movie is selected
    if selected_movie_name:
        st.image(fetch_poster_by_title(selected_movie_name), width=200, caption=selected_movie_name)
with col2:
    recommend_clicked = st.button("🎯 Recommend", use_container_width=True)


# SESSION STATE INIT

if "page" not in st.session_state:
    st.session_state.page = 1
if "names" not in st.session_state:
    st.session_state.names = []
    st.session_state.posters = []


# HANDLE RECOMMENDATION

if recommend_clicked:
    st.session_state.names, st.session_state.posters = recommend(selected_movie_name)
    st.session_state.page = 1


# SHOW RECOMMENDATIONS

if st.session_state.names:
    total_pages = (len(st.session_state.names) + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE

    col_prev, _, col_next = st.columns([1, 8, 1])
    with col_prev:
        if st.button("⬅ Previous", use_container_width=True, disabled=(st.session_state.page == 1)):
            st.session_state.page -= 1
    with col_next:
        if st.button("Next ➡", use_container_width=True, disabled=(st.session_state.page == total_pages)):
            st.session_state.page += 1

    start_idx = (st.session_state.page - 1) * MOVIES_PER_PAGE
    end_idx = start_idx + MOVIES_PER_PAGE
    page_names = st.session_state.names[start_idx:end_idx]
    page_posters = st.session_state.posters[start_idx:end_idx]

    for row_start in range(0, len(page_names), MOVIES_PER_ROW):
        cols = st.columns(MOVIES_PER_ROW)
        for idx, col in enumerate(cols):
            movie_idx = row_start + idx
            if movie_idx < len(page_names):
                with col:
                    st.markdown(f"""
                        <div class="movie-card">
                            <img src="{page_posters[movie_idx]}" width="80%" style="border-radius: 10px;">
                            <div class="movie-title">{page_names[movie_idx]}</div>
                        </div>
                    """, unsafe_allow_html=True)
