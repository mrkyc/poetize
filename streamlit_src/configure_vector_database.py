import streamlit as st
import tarfile
import shutil
import gdown
import os

from streamlit_src.utils import stream_text


# Add a title to the page
st.title("Welcome to the Poetize app!")

# Define the second welcome text
second_welcome_text = """
    Please select one of the available vector databases from which you would like to retrieve information.

    This database will be used to retrieve song fragments that are meaningfully similar to the phrase you enter.
    Using the Retrieval-Augmented Generation (RAG) method, the app will craft a unique, creative poem for you.
    
    Due to resource limitations on the Streamlit Cloud, there isn't a single, comprehensive vector database.
    Instead, there is a curated selection of databases to ensure optimal performance and responsiveness.
    Basically, you can randomly choose one and let's start the creativity flow!

    If you have already downloaded the database, you can select the first option to use it.
    """

# Check if the second welcome text stream executed variable exists in the session state
if "second_welcome_text_stream_executed" not in st.session_state:
    st.session_state["second_welcome_text_stream_executed"] = False

# Check if the second welcome text stream has been executed
# If not, display the text using the stream_data function and set the flag to True
# Otherwise, display the text normally
if not st.session_state["second_welcome_text_stream_executed"]:
    st.write_stream(stream_text(second_welcome_text))
    st.session_state["second_welcome_text_stream_executed"] = True
else:
    st.write(second_welcome_text)

# Define the available vector databases
options = [
    "Use the already downloaded database",
    "Vector database number 1",
    "Vector database number 2",
    "Vector database number 3",
    "Vector database number 4",
    "Vector database number 5",
]

# Add a selectbox for the user to choose the vector database part number to use
selected_chroma_db_part = st.selectbox(
    "Select a vector database to use",
    options=options,
)

# Store the selected vector database part number in the session state
chroma_db_part = options.index(selected_chroma_db_part)

# Store the selected vector database part number in the session state
st.session_state["chroma_db_part"] = chroma_db_part

# Add a start button to download and extract the selected vector database
if st.button("START!", use_container_width=True):

    # Check if the selected vector database part number is 6 (use the already downloaded database)
    if chroma_db_part == 0:

        # If the database is not downloaded, display a warning message and stop the execution
        if not os.path.exists("chroma_db"):
            st.warning("There is no database downloaded yet!", icon="⚠")
            st.stop()

    # Otherwise, download and extract the selected vector database
    else:
        # Url from the secrets file with a link to the selected vector database
        url = st.secrets[f"CHROMA_DB_PART{chroma_db_part}_LINK"]

        # Download the selected vector database and extract it
        destination = "chroma_db.tar.gz"
        with st.spinner("Downloading the database..."):
            gdown.download(url, destination, quiet=True)
        with st.spinner("Extracting the database..."):
            with tarfile.open(destination, "r:gz") as tar:
                tar.extractall()

        # Remove the chroma_db folder if it already exists
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")

        # Rename the extracted folder to chroma_db and remove the downloaded .tar.gz file
        os.rename(f"chroma_db_part{chroma_db_part}", "chroma_db")
        os.remove(destination)

    # Switch to the next page
    st.switch_page(os.path.join("streamlit_src", "poetize.py"))
