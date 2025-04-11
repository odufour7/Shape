"""Write about text."""

import streamlit as st


def about() -> None:
    """Write about text."""
    text = """

    ### Overview
    Project shape
    """
    st.markdown(text)
    text2 = """
    This app is part of the SHAPE project.
    """
    st.markdown(text2)

    text3 = " Link towards C++, article, examples of using"
    st.markdown(text3)
