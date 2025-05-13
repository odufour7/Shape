"""
Main file to run the application.

This script initializes the application, sets up the user interface, and determines
which functionality to execute based on the selected tab in the sidebar.

The application includes various tabs for different functionalities, such as:
    - `One agent` (for 2D/3D agent creation and visualisation)
    - `Crowd` (for 2D/3D crowd creation, visualisation, and generation of .xml config files)
    - `Anthropometry` (for data analysis)
    - `About` (for displaying information about the project)

Examples
--------
To run the application, execute these commands from the root directory of the project:

>>> pip install uv
>>> uv sync
>>> uv run streamlit run src/streamlit_app/app/app.py
"""

import streamlit_app.utils.constants as cst_app
from configuration.data import datafactory
from streamlit_app.app import documentation, ui
from streamlit_app.tabs.anthropometry_tab import run_tab_anthropometry
from streamlit_app.tabs.crowd_creation_tab import run_tab_crowd
from streamlit_app.tabs.one_agent_tab import run_tab_one_agent
from streamlit_app.utils.logging import setup_logging

setup_logging()
if __name__ == "__main__":
    ui.setup_app()
    selected_tab = ui.menubar()
    ui.init_app_looks()
    datafactory.prepare_data()

    if selected_tab == cst_app.FIRST_TAB_NAME:
        run_tab_one_agent()

    if selected_tab == cst_app.SECOND_TAB_NAME:
        run_tab_crowd()

    if selected_tab == cst_app.THIRD_TAB_NAME:
        run_tab_anthropometry()

    if selected_tab == cst_app.FOURTH_TAB_NAME:
        documentation.about()
