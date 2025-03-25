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

import shapes.utils.constants as cst
from shapes.datafactory import datafactory
from shapes.docs import docs
from shapes.tabs.agent2D_tab import run_tab_agent2D
from shapes.tabs.anthropometry_tab import run_tab_anthropometry
from shapes.tabs.crowd_tab import run_tab_crowd
from shapes.tabs.custom_crowd_tab import run_tab_custom_crowd
from shapes.tabs.pedestrian3D_tab import run_tab_pedestrian3D
from shapes.ui import ui
from shapes.utils.logging_custom import setup_logging

setup_logging()
if __name__ == "__main__":
    ui.setup_app()
    selected_tab = ui.init_sidebar()
    datafactory.prepare_data()

    if selected_tab == cst.FIRST_TAB_NAME:
        docs.about()

    if selected_tab == cst.SECOND_TAB_NAME:
        run_tab_agent2D()

    if selected_tab == cst.THIRD_TAB_NAME:
        run_tab_pedestrian3D()

    if selected_tab == cst.FOURTH_TAB_NAME:
        run_tab_anthropometry()

    if selected_tab == cst.FIFTH_TAB_NAME:
        run_tab_crowd()

    if selected_tab == cst.SIXTH_TAB_NAME:
        run_tab_custom_crowd()
