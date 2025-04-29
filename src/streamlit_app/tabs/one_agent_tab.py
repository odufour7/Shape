"""Streamlit tab for visualizing a single agent in 2D or 3D."""

import streamlit as st

from streamlit_app.tabs.one_agent_2D import run_tab_agent2D
from streamlit_app.tabs.one_pedestrian_3D import run_tab_pedestrian3D


def run_tab_one_agent() -> None:
    """
    Run the 2D agent visualization tab.

    This function initializes the session state, creates sliders for agent measures,
    and handles the main page content for visualizing a single agent in 2D.
    """
    st.subheader("Select the dimension of the agent representation")
    dimension_options = {
        "2D": "2D",
        "3D": "3D",
    }
    selected_dimension_options = st.pills(" ", list(dimension_options.values()), label_visibility="collapsed")

    if selected_dimension_options == dimension_options["2D"]:
        run_tab_agent2D()
    elif selected_dimension_options == dimension_options["3D"]:
        run_tab_pedestrian3D()
