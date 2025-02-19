from pathlib import Path

import streamlit as st


def about() -> None:
    """Write About text."""
    path = Path(__file__)
    ROOT_DIR = path.parent.parent.parent.absolute()
    img_path_1 = ROOT_DIR / "data" / "images" / "example.png"
    text = """

    ## Overview
    Project shape
    """
    st.markdown(text)
    st.image(str(img_path_1), width=300, caption="Example.")
    text2 = """
    This app is part of the SHAPE project.
    """
    st.markdown(text2)
