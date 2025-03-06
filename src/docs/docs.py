"""Write about text."""

import streamlit as st


def about() -> None:
    """Write About text."""
    text = """

    ### Overview
    Project shape
    """
    st.markdown(text)
    text2 = """
    This app is part of the SHAPE project.
    """
    st.markdown(text2)

    text3 = " Lien vers code C++, article, exemples d'utilisation"
    st.markdown(text3)
