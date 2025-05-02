"""User interface module."""

from pathlib import Path
from typing import Any

import streamlit as st
from streamlit_option_menu import option_menu

import streamlit_app.utils.constants as cst_app


def setup_app() -> None:
    """Set up the Streamlit page configuration."""
    st.set_page_config(
        page_title=f"{cst_app.PROJECT_NAME} Project",
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/odufour7/Shape",
            "Report a bug": "https://github.com/odufour7/Shape/issues",
            "About": f"# {cst_app.PROJECT_NAME} Project " + ":flag-fr:",
        },
    )


def menubar() -> Any:
    """
    Initialize the sidebar for the Shape project application.

    This function applies custom CSS rules to handle multi-line text alignment and indentation
    and creates a sidebar menu with multiple tabs and icons. To add more tabs, update the list
    of tab names and icons using resources from https://icons.getbootstrap.com/.

    Returns
    -------
    Any
        The selected option from the sidebar menu.

    Notes
    -----
    - Streamlit's `st.markdown` is used to apply custom CSS styles.
    - The `option_menu` function creates the sidebar menu with specified tabs and icons.
    - The `unsafe_allow_html=True` parameter enables Streamlit to render raw HTML and CSS.
    - The `styles` dictionary customizes the appearance of the sidebar menu.
    """
    # Custom CSS rules to handle multi-line text alignment and indentation, that applies to the entire app.
    st.markdown(
        """
        <style>
        .nav-link {
            display: flex;
            align-items: center;
            white-space: pre-wrap; /* Ensures that long text wraps onto multiple lines without breaking formatting */
            text-align: left;
        }
        .nav-link div {
            margin-left: 10px; /* Adjust margin to align text with icon */
        }
        .nav-link div span {
            display: block;
            padding-left: 20px; /* Simulate tab space */
        }
        </style>
        """,
        unsafe_allow_html=True,  # enables Streamlit to render raw HTML and CSS
    )
    return option_menu(
        f"{cst_app.PROJECT_NAME} project",
        [
            cst_app.FIRST_TAB_NAME,
            cst_app.SECOND_TAB_NAME,
            cst_app.THIRD_TAB_NAME,
            cst_app.FOURTH_TAB_NAME,
        ],
        icons=[
            "person-fill",
            "people-fill",
            "bar-chart-line",
            "info-square",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",  # Removes padding from container. (generate space around an element's content)
                "background-color": "#fafafa",  # Sets the background color of the container to a light gray shade (#fafafa).
            },
            "icon": {"color": "red", "font-size": "15px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#fafafa",  # Sets the hover color to a light gray shade (#eee).
            },
        },
    )


def init_app_looks() -> None:
    """
    Initialize the appearance of the application.

    This function sets up the sidebar with a GitHub repository badge, a DOI badge,
    and a logo image. It constructs the paths and URLs required for these elements
    and uses Streamlit's sidebar components to display them.

    - Displays a GitHub repository badge with a link to the repository.
    - Displays a DOI badge with a link to the DOI.
    - Displays a logo image from the assets directory.
    """
    current_file_path = Path(__file__)
    ROOT_DIR = current_file_path.parent.parent.parent.parent.absolute()
    logo_path = ROOT_DIR / "docs" / "source" / "_static" / "logo" / "art_light_logo_app.png"
    article_badge = "[![](https://badgen.net/badge/DOI/open%20access/orange)](https://scipost.org/SciPostPhysCodeb)"
    doc_badge = "[![](https://badgen.net/static/DOC/shapes-docs/cyan?icon=https://icons.getbootstrap.com/icons/filetype-doc/)](https://shapes-crowd.readthedocs.io/en/latest/index.html)"
    gh = "https://badgen.net/badge/icon/GitHub?icon=github&label"
    repo = "https://github.com/odufour7/Shape"
    repo_badge = f"[![]({gh})]({repo})"

    c1, c2 = st.sidebar.columns((0.25, 0.8))
    c1.write("**Article**")
    c2.write(article_badge)
    c1.write("**Doc**")
    c2.write(doc_badge)
    c1.write("**Repo**")
    c2.markdown(repo_badge, unsafe_allow_html=True)

    st.sidebar.image(str(logo_path), use_container_width=True)

    st.sidebar.warning("⚠️ All measurements in this app are displayed in centimeters.")
