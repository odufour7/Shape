from src.docs import docs
from src.tabs.anthropometry_tab import run_tab_anthropometry
from src.tabs.crowd_tab import run_tab_crowd
from src.tabs.pedestrian2D_tab import run_tab_pedestrian2D
from src.tabs.pedestrian3D_tab import run_tab_pedestrian3D
from src.ui import ui

if __name__ == "__main__":
    ui.setup_app()
    selected_tab = ui.init_sidebar()

    if selected_tab == "About":
        docs.about()

    if selected_tab == "Pedestrian 2D":
        run_tab_pedestrian2D()

    if selected_tab == "Pedestrian 3D":
        run_tab_pedestrian3D()

    if selected_tab == "Crowd":
        run_tab_crowd()

    if selected_tab == "Anthropometry":
        run_tab_anthropometry()
