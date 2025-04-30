import streamlit as st
import pandas as pd
import altair as alt

def render_model_score_chart(row):
    model_scores = {
        "GPT-3.5": row["gpt35_score"],
        "GPT-4o": row["gpt4o_score"],
        "Claude": row["claude_score"],
        "Gemini": row["gemini_score"],
        "LLaMA 8B": row["llama8b_score"],
        "LLaMA 70B": row["llama70b_score"]
    }
    score_df = pd.DataFrame(model_scores.items(), columns=["Model", "Score"])
    chart = alt.Chart(score_df).mark_bar().encode(
        x="Model", y="Score", color="Model", tooltip=["Model", "Score"]
    ).properties(height=250)
    st.altair_chart(chart, use_container_width=True)

def render_query_table(query_df, book_title):
    # Filter for the selected book
    book_queries = query_df[query_df["book_title"] == book_title].copy()

    # Select relevant columns
    model_cols = [
        "gpt35_answer", "gpt4o_answer", "claude_answer",
        "gemini_answer", "llama8b_answer", "llama70b_answer"
    ]
    base_cols = ["query_id", "query", "correct_answer"]
    display_df = book_queries[base_cols + model_cols].reset_index(drop=True)

    # Define cell styling function
    def highlight_correct(val, correct):
        if pd.isna(val):
            return "background-color: gray"
        elif val.strip().lower() == correct.strip().lower():
            return "background-color: #228B22"  # light green
        else:
            return "background-color: #B22222"  # light red

    # Apply style based on comparison to correct_answer
    def style_row(row):
        return [
            "" if col not in model_cols else highlight_correct(row[col], row["correct_answer"])
            for col in display_df.columns
        ]

    styled_df = display_df.style.apply(style_row, axis=1)

    with st.expander("🔎 Show detailed model responses"):
        st.dataframe(styled_df, use_container_width=True)
