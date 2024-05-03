import streamlit as st
import time
import os

from streamlit_src.utils import stream_text, validate_api_key


# Add a title to the page
st.title("Welcome to the Poetize app!")

# Define the first welcome text
first_welcome_text = """
    To get started, please enter your OpenAI API key below.
    This key will allow the app to connect with OpenAI's services to generate embeddings from the phrases you enter, as well as to create unique text based on those embeddings.
    """

# Check if the first welcome text stream executed variable exists in the session state
if "first_welcome_text_stream_executed" not in st.session_state:
    st.session_state["first_welcome_text_stream_executed"] = False

# Check if the first welcome text stream has been executed
# If not, display the text using the stream_data function and set the flag to True
# Otherwise, display the text normally
if not st.session_state["first_welcome_text_stream_executed"]:
    st.write_stream(stream_text(first_welcome_text))
    st.session_state["first_welcome_text_stream_executed"] = True
else:
    st.write(first_welcome_text)

# Check if the OpenAI API key variable exists in the session state
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = None

# Add a text input field for the user to enter their OpenAI API key
openai_api_key = st.text_input(
    "OpenAI API Key",
    type="password",
    autocomplete="off",
)

# Add a submit button to validate the OpenAI API key
# If the key is valid, store it in the session state and switch to the next page
if st.button(
    "Submit",
    use_container_width=True,
):
    # Admin option to not enter the OpenAI API key and use the password instead
    if openai_api_key == st.secrets["PASSWORD"]:
        openai_api_key = st.secrets["OPENAI_API_KEY"]

    # Validate the OpenAI API key
    # If the key is valid, store it in the session state and switch to the next page
    # Otherwise, display a warning message
    if not validate_api_key(openai_api_key):
        st.warning("Please enter your valid OpenAI API key!", icon="⚠")
    else:
        st.session_state["openai_api_key"] = openai_api_key
        st.success("OpenAI API Key has been entered!")
        time.sleep(1)
        st.switch_page(os.path.join("streamlit_src", "configure_vector_database.py"))
