"""Documentation page for the app."""

from pathlib import Path

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

    current_file_path = Path(__file__)
    ROOT_DIR = current_file_path.parent.parent.parent.parent.absolute()
    logo_path = ROOT_DIR / "data" / "images" / "coverage_explanation.png"
    st.image(str(logo_path), use_container_width=True)
