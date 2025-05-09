"""Documentation page for the app."""

from pathlib import Path

import streamlit as st

from streamlit_app.utils import constants as cst_app


def about() -> None:
    """Write about text."""
    text = f"""

    ### Overview
    {cst_app.PROJECT_NAME} shape
    """
    st.markdown(text)

    current_file_path = Path(__file__)
    ROOT_DIR = current_file_path.parent.parent.parent.parent.absolute()
    logo_path = ROOT_DIR / "data" / "images" / "coverage_explanation.png"
    st.image(str(logo_path), use_container_width=True)
