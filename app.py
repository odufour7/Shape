"""Main file to run the application."""

import src.utils.constants as cst
from src.datafactory import datafactory
from src.docs import docs
from src.tabs.agent2D_tab import run_tab_agent2D
from src.tabs.anthropometry_tab import run_tab_anthropometry
from src.tabs.crowd_tab import run_tab_crowd
from src.tabs.custom_crowd_tab import run_tab_custom_crowd
from src.tabs.pedestrian3D_tab import run_tab_pedestrian3D
from src.ui import ui

if __name__ == "__main__":
    ui.setup_app()
    selected_tab = ui.init_sidebar()
    datafactory.prepare_anthropometric_data()

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
