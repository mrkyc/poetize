import streamlit as st
import os


pages = [
    st.Page(os.path.join("streamlit_src", "poetize.py"), title="Poetize", icon="📜"),
    st.Page(
        os.path.join("streamlit_src", "configure_openai_api_key.py"),
        title="Configure OpenAI API Key",
        icon="🔑",
    ),
    st.Page(
        os.path.join("streamlit_src", "configure_vector_database.py"),
        title="Configure Vector Database",
        icon="🗄",
    ),
]

pg = st.navigation(pages, position="hidden")
pg.run()
