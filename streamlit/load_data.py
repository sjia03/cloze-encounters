import pandas as pd
import streamlit as st

@st.cache_data
def load_books():
    return pd.read_csv("https://www.dropbox.com/scl/fi/xyq5ssz2zh7ur16dd2ems/book-level-stella.csv?rlkey=rb49nkeo5lmdgsshx5010jx4h&st=uprgwdfp&dl=1")

@st.cache_data
def load_queries():
    return pd.read_csv("https://www.dropbox.com/scl/fi/bubxu12hfgi7uy90bb489/query-level-final.csv?rlkey=ullvil087abk7igmhb7pvo4p3&st=e9tdqivw&dl=1")