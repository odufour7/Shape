"""Pedestrian Visualization Tab"""

from io import BytesIO

import streamlit as st
from shapely.geometry import Polygon

import src.utils.constants as cst
from src.classes.trial.crowd_old import Crowd
from src.plotting import plot


def main() -> None:
    """Main function for the crowd tab."""

    st.info(
        "The computation of the random packing of the crowd is ongoing and may take some time.\n"
        "Please be patient.",
        icon="⏳",
    )

    current_room_geometry = Polygon(
        [
            (0, 0),
            (cst.DEFAULT_BOUNDARY_X, 0),
            (cst.DEFAULT_BOUNDARY_X, cst.DEFAULT_BOUNDARY_Y),
            (0, cst.DEFAULT_BOUNDARY_Y),
        ]
    )  # Example room geometry

    current_crowd = Crowd(
        density=cst.DEFAULT_DENSITY,
        boundaries=current_room_geometry,
        chest_depth=(cst.DEDAULT_MEAN_CHEST_DEPTH, cst.DEDAULT_STD_CHEST_DEPTH),
        bideltoid_breadth=(
            cst.DEDAULT_MEAN_BIDELTOID_BREADTH,
            cst.DEDAULT_STD_BIDELTOID_BREADTH,
        ),
    )

    interpenetration = current_crowd.calculate_interpenetration()
    if interpenetration > 1e-4:
        st.warning(
            f"The asked density seems too high.\n"
            f"The interpenetration area is {interpenetration:.3f} m².\n"
            "Please try again or lower the density.",
            icon="⚠️",
        )

    st.sidebar.header("Adjust parameters")

    # Main Page Content
    st.subheader("Visualisation")
    col1, _ = st.columns([1.5, 1])  # Adjust proportions as needed
    with col1:
        fig = plot.display_crowd2D(current_crowd)
        st.pyplot(fig)
        # Save the figure to a BytesIO object in PDF format
        crowd_plot = BytesIO()
        fig.savefig(crowd_plot, format="pdf")
        crowd_plot.seek(0)  # Reset buffer pointer to the beginning
        # Streamlit button in the sidebar to download the graph in PDF format
        st.sidebar.header("Download")
        st.sidebar.download_button(
            label="Download Image",
            data=crowd_plot,
            file_name="crowd.pdf",
            mime="application/pdf",
        )


def run_tab_crowd() -> None:
    """Function to run the crowd tab."""
    main()
