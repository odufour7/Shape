"""
Main file to run the application.

This script initializes the application, sets up the user interface, and determines
which functionality to execute based on the selected tab in the sidebar.

The application includes various tabs for different functionalities, such as:
    - Agent 2D creation and display
    - 3D pedestrian creation and display
    - Anthropometry analysis
    - Crowd creation and display
    - Custom crowd creation and display

See Also
--------
shapes.utils.constants
    Provides constants used throughout the application.
shapes.datafactory
    Handles data preparation and management.
shapes.docs
    Contains documentation-related utilities.
shapes.tabs
    Modules implementing functionality for individual tabs.
shapes.ui
    Manages the user interface of the application.

Examples
--------
To run the application, execute these commands directly:

>>> pip install uv
>>> uv sync
>>> uv run streamlit src/app.py
"""

import streamlit_app.utils.constants as cst_app
from configuration.data import datafactory
from streamlit_app.app import documentation, ui
from streamlit_app.tabs.agent2D_tab import run_tab_agent2D
from streamlit_app.tabs.anthropometry_tab import run_tab_anthropometry
from streamlit_app.tabs.auto_crowd_creation_tab import run_tab_crowd
from streamlit_app.tabs.manual_crowd_creation_tab import run_tab_custom_crowd
from streamlit_app.tabs.pedestrian3D_tab import run_tab_pedestrian3D
from streamlit_app.utils.logging import setup_logging

setup_logging()
if __name__ == "__main__":
    ui.setup_app()
    selected_tab = ui.init_sidebar()
    datafactory.prepare_data()

    if selected_tab == cst_app.FIRST_TAB_NAME:
        documentation.about()

    if selected_tab == cst_app.SECOND_TAB_NAME:
        run_tab_agent2D()

    if selected_tab == cst_app.THIRD_TAB_NAME:
        run_tab_pedestrian3D()

    if selected_tab == cst_app.FOURTH_TAB_NAME:
        run_tab_anthropometry()

    if selected_tab == cst_app.FIFTH_TAB_NAME:
        run_tab_crowd()

    if selected_tab == cst_app.SIXTH_TAB_NAME:
        run_tab_custom_crowd()
