# To deal with error: 'Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.'
__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import streamlit as st
import os

from streamlit_src.utils import (
    get_similar_documents,
    generate_response,
    stream_response,
)


# Add a title to the page
st.title("Let's poetize your thoughts!")

# Check if the OpenAI API key exist in the session state
# If not, redirect the user to the OpenAI API key configuration page
if (
    "openai_api_key" not in st.session_state
    or st.session_state["openai_api_key"] is None
):
    st.switch_page(os.path.join("streamlit_src", "configure_openai_api_key.py"))

# Check if the chroma db database is selected and exists in the session state
# If not, redirect the user to the vector database configuration page
elif (
    "chroma_db_part" not in st.session_state
    or st.session_state["chroma_db_part"] is None
):
    st.switch_page(os.path.join("streamlit_src", "configure_vector_database.py"))

# Create a form widget
with st.form("phrase_form"):

    # Create a text area widget to get the user input for the phrase used to generate the poem
    query = st.text_area(
        "Share your thoughts!",
        placeholder="Enter a phrase to generate a poem from...",
        max_chars=250,
    )

    # Create a slider widget to get the user input for the temperature of the poem generation
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Temperature controls the randomness of the generated text. Lower values will result in more predictable text, while higher values will result in more creative text. Default: 0.5",
    )

    # Create a text input widget to get the user input for the language of the poem
    prompt_lang = st.text_input(
        "Poem language",
        value="English",
        help="The language in which the poem should be written. Default: English",
    )

    # Create a submit button widget to submit the form
    if st.form_submit_button("Submit", use_container_width=True):

        # If the user input is empty, show a warning message and stop the execution
        if query == "":
            st.warning("Please enter a phrase to continue!", icon="⚠")
            st.stop()

        # Get the similar documents based on the user input
        similar_documents = get_similar_documents(query)

        # Display the matched lyrics fragments in an expander widget
        with st.expander("Display matched lyrics fragments"):
            for doc in similar_documents.values():
                text_to_display = f"""
                **Artist**: {doc["artist"]}  
                **Title**: {doc["title"]}  
                **Matched lyrics fragment**: {doc["lyrics_fragment"]}
                """
                st.markdown(text_to_display)

        # Generate the response poem based on the user input and the matched lyrics fragments
        response = generate_response(prompt_lang, similar_documents, temperature)

        # Display the response poem
        with st.container(border=True):
            st.subheader("A poem for you!")
            st.write_stream(stream_response(response))
