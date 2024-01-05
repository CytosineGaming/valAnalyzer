import streamlit as st

st.set_page_config(
    page_title = "Match"
)

match_id = st.experimental_get_query_params()

st.write(match_id)