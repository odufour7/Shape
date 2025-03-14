"""Main file to run the application."""

import src.shapes_package.utils.constants as cst
from src.shapes_package.datafactory import datafactory
from src.shapes_package.docs import docs
from src.shapes_package.tabs.agent2D_tab import run_tab_agent2D
from src.shapes_package.tabs.anthropometry_tab import run_tab_anthropometry
from src.shapes_package.tabs.crowd_tab import run_tab_crowd
from src.shapes_package.tabs.custom_crowd_tab import run_tab_custom_crowd
from src.shapes_package.tabs.pedestrian3D_tab import run_tab_pedestrian3D
from src.shapes_package.ui import ui
from src.shapes_package.utils.logging_custom import setup_logging

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
