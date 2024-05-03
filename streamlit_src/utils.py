from chromadb import PersistentClient
from openai import OpenAI
import streamlit as st
import openai
import time
import os

from streamlit_src.constants import (
    CHAT_MODEL_NAME,
    EMBEDDING_MODEL_NAME,
    MAX_TOKENS,
    N_SIMILAR_DOCUMENTS,
)


def stream_text(text):
    """
    Stream text to the UI in real-time.

    Parameters:
    ----------
    text : str
        The text to stream to the UI.

    Yields:
    -------
    letter : str
        The letter to stream to the UI with a delay of 0.01 seconds.
    """

    for letter in text.split(" "):
        yield letter + " "
        time.sleep(0.01)


def stream_response(response):
    """
    Stream the response to the UI in real-time.

    Parameters:
    ----------
    response : dict
        The response from the OpenAI chat model.

    Yields:
    -------
    chunk : str
        The chunk of the response to stream to the UI with a delay of 0.01 seconds.
    """

    for chunk in response:
        yield chunk.choices[0].delta.content or ""
        time.sleep(0.01)


def validate_api_key(api_key):
    """
    Validate the OpenAI API key entered by the user.

    Parameters:
    ----------
    api_key : str
        The OpenAI API key entered by the user.

    Returns:
    -------
    is_valid : bool
        True if the API key is valid, False otherwise.
    """

    if api_key == "":
        return False
    try:
        openai.api_key = api_key
        client = openai.OpenAI(api_key=api_key)
        client.models.list()
        return True
    except openai.AuthenticationError:
        return False


@st.cache_resource(show_spinner=False)
def get_openai_client():
    """
    Get the OpenAI client.

    Returns:
    -------
    client : OpenAI
        The OpenAI client.
    """

    return OpenAI(api_key=st.session_state["openai_api_key"])


def get_embeddings(text):
    """
    Get the embeddings for the input text.

    Parameters:
    ----------
    text : str
        The input text to get the embeddings.

    Returns:
    -------
    embeddings : dict
        The embeddings for the input text.
    """

    client = get_openai_client()
    return client.embeddings.create(input=text, model=EMBEDDING_MODEL_NAME)


def get_chromadb_collection():
    """
    Get the ChromaDB collection.

    Returns:
    -------
    collection : dict
        The ChromaDB collection.
    """

    client = PersistentClient(path="chroma_db")
    try:
        collection = client.get_collection(name="lyrics")
        return collection
    except Exception as e:
        st.error(f"Error occurred while loading the collection")
        st.stop()


def format_query_results(query_results):
    """
    Format the query results.

    Parameters:
    ----------
    query_results : dict
        The query results from the ChromaDB collection.

    Returns:
    -------
    similar_documents : dict
        The collection of similar documents.
    """

    similar_documents = {}
    for i, id in enumerate(query_results["ids"][0]):
        similar_documents[id] = {
            "artist": query_results["metadatas"][0][i]["artist"],
            "title": query_results["metadatas"][0][i]["title"],
            "lyrics_fragment": query_results["documents"][0][i],
            "distance": query_results["distances"][0][i],
        }
    return similar_documents


def get_similar_documents(text):
    """
    Get similar documents based on the input text.

    Parameters:
    ----------
    text : str
        The input text to find similar documents.

    Returns:
    -------
    collection : dict
        The collection of similar documents.
    """

    embeddings = get_embeddings(text)
    collection = get_chromadb_collection()
    query_results = collection.query(
        query_embeddings=embeddings.data[0].embedding,
        n_results=N_SIMILAR_DOCUMENTS,
        include=["metadatas", "documents", "distances"],
    )
    return format_query_results(query_results)


def generate_response(prompt_lang, prompt_docs, temperature):
    """
    Generate a response from the OpenAI chat model.

    Parameters:
    ----------
    prompt_lang : str
        The language in which the poem should be written.
    prompt_docs : dict
        A dictionary containing the lyrics fragments.
    temperature : float
        The temperature of the poem generation.

    Returns:
    -------
    response : dict
        The response from the OpenAI chat model.
    """

    prompt = "\n\nNext fragment:\n".join(
        [doc["lyrics_fragment"].replace("\n", ". ") for doc in prompt_docs.values()]
    )

    client = get_openai_client()
    response = client.chat.completions.create(
        model=CHAT_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": f"""
                    You are a talented poet.
                    Your task is to create a poem using as many phrases and words as possible from the textual data provided.
                    The input consists of fragments of song lyrics, which should be transformed into a coherent and artistic poem.
                    Exclude any parts of the input that are not suitable for poetic expression, such as brackets, chorus lines, sound effects (e.g., 'woah' or 'la la la'), or redundant repetitions.
                    The poem should be at least 10 lines long.
                    You must ensure that the poem ends with a complete sentence with proper punctuation.
                    At the end of each line, place two spaces.
                    The poem must be original and not a verbatim copy of the input.
                    The poem must be written exclusively in {prompt_lang} language.
                    """,
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_completion_tokens=MAX_TOKENS,
        n=1,
        stream=True,
    )
    return response
