"""Pedestrian Visualization Tab"""

from io import BytesIO

import streamlit as st
from shapely.geometry import Polygon

# import src.utils.constants as cst
from src.classes.crowd import Crowd
from src.plotting import plot


def main() -> None:

    current_room_geometry = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])  # Example room geometry
    current_crowd = Crowd(
        density=13e-4,
        geometry=current_room_geometry,
        chest_depth=(15.0, 5.0),
        bideltoid_breadth=(25.0, 5.0),
        crowd_orientation=(0.0, 0.5),
    )
    # Main Page Content
    st.title("Crowd Visualization")
    if st.button("Draw a Crowd"):

        fig = plot.display_crowd2D(current_crowd)

        st.pyplot(fig)
        # Save the figure to a BytesIO object in PDF format
        crowd_plot = BytesIO()
        fig.savefig(crowd_plot, format="pdf")
        crowd_plot.seek(0)  # Reset buffer pointer to the beginning

        # Streamlit button in the sidebar to download the graph in PDF format
        st.sidebar.download_button(
            label="Download Image",
            data=crowd_plot,
            file_name="crowd.pdf",
            mime="application/pdf",
        )


def run_tab_crowd() -> None:
    """
    Execute the main function for the survey tab.

    This function serves as the entry point for running the 2D pedestrian tab
    functionality within the application. It calls the main() function
    to initiate the necessary processes.
    """
    main()
