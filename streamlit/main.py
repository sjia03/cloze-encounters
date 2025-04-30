# streamlit_app.py

import streamlit as st
from load_data import load_books, load_queries
from components import render_model_score_chart, render_query_table
import pandas as pd
import altair as alt

# Must be the first Streamlit command
st.set_page_config(page_title="Cloze Encounters: Find Name Cloze Score by Book", layout="wide")

# Load data
book_df = load_books()
query_df = load_queries()

st.title("📚 Cloze Encounters: Find Name Cloze Score by Book")

# --- Sidebar Search ---
with st.sidebar:
    st.header("🔍 Search Filters")
    search_title = st.text_input("Search by Title")
    search_author = st.text_input("Search by Author")
    genre_filter = st.selectbox("Select Genre", ["All", "Fiction", "Nonfiction"])

# --- Filtering ---
filtered_df = book_df.copy()

if search_title:
    filtered_df = filtered_df[filtered_df["book_title"].str.contains(search_title, case=False, na=False)]

if search_author:
    filtered_df = filtered_df[filtered_df["author"].str.contains(search_author, case=False, na=False)]

if genre_filter == "Fiction":
    filtered_df = filtered_df[filtered_df["fiction"] == 1]
elif genre_filter == "Nonfiction":
    filtered_df = filtered_df[filtered_df["nonfiction"] == 1]

# --- Display Results ---
if search_title or search_author or genre_filter != "All":
    if filtered_df.empty:
        st.warning("No books found. Try a different query.")
    else:
        for _, row in filtered_df.iterrows():
            st.subheader(row["book_title"])
            st.markdown(f"**Author:** {row['author']}")
            st.markdown(f"**Published:** {row['pub_year']}")
            st.markdown(f"**In Books3:** {'✅' if row['in_books3'] else '❌'}")
            st.markdown(f"**Genres:** {row['genres']}")
            st.markdown(f"**Rating:** ⭐ {row['avg_rating']} (from {row['num_ratings']} ratings)")

            # Model scores visualization
            render_model_score_chart(row)

            # Expandable detailed view
            render_query_table(query_df, row["book_title"])

            st.divider()

else:
    # Homepage visuals if no search is active
    st.info("Use the sidebar to search for books by title, author, or genre.")
    st.subheader("📈 Dataset Overview")

    # Score distribution across models
    score_cols = ["gpt35_score", "gpt4o_score", "claude_score", "gemini_score", "llama8b_score", "llama70b_score"]
    score_long_df = book_df[score_cols].melt(var_name="Model", value_name="Score")
    model_name_map = {
        "gpt35_score": "GPT-3.5",
        "gpt4o_score": "GPT-4o",
        "claude_score": "Claude",
        "gemini_score": "Gemini",
        "llama8b_score": "LLaMA 8B",
        "llama70b_score": "LLaMA 70B"
    }
    score_long_df["Model"] = score_long_df["Model"].map(model_name_map)

    chart = (
        alt.Chart(score_long_df)
        .transform_filter(alt.datum.Score != None)
        .mark_area(opacity=0.4)
        .encode(
            x=alt.X("Score", bin=alt.Bin(maxbins=50), title="Model Score"),
            y=alt.Y("count()", stack=None),
            color="Model:N",
            tooltip=["Model", "count()"]
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    # Genre distribution
    genre_counts = pd.DataFrame({
        "Genre": ["Fiction", "Nonfiction"],
        "Count": [book_df["fiction"].sum(), book_df["nonfiction"].sum()]
    })

    st.markdown("**Fiction vs Nonfiction**")
    pie_chart = (
        alt.Chart(genre_counts)
        .mark_arc()
        .encode(
            theta="Count",
            color="Genre",
            tooltip=["Genre", "Count"]
        )
        .properties(height=300)
    )
    st.altair_chart(pie_chart, use_container_width=True)

    # Publication year
    st.markdown("**Books by Publication Year**")
    pub_year_counts = book_df["pub_year"].value_counts().sort_index()
    st.line_chart(pub_year_counts)
