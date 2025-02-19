"""Pedestrian Visualization Tab"""

from io import BytesIO

import streamlit as st

import src.utils.constants as cst
from src.classes.pedestrian import Pedestrian
from src.plotting import plot


def main() -> None:

    current_pedestrian = Pedestrian(
        chest_depth=cst.DEFAULT_CHEST_DEPTH,
        bideltoid_breadth=cst.DEFAULT_BIDELTOID_BREADTH,
        height=cst.DEFAULT_HEIGHT,
        sex=cst.DEFAULT_SEX,
    )

    # Sidebar Sliders for Anthropometric Parameters
    st.sidebar.header("Adjust Parameters")
    bideltoid_breadth = st.sidebar.slider(
        "Bideltoid Breadth (cm)",
        min_value=cst.MIN_BIDELTOID_BREADTH,
        max_value=cst.MAX_BIDELTOID_BREADTH,
        value=cst.DEFAULT_BIDELTOID_BREADTH,
        step=1.0,
    )
    chest_depth = st.sidebar.slider(
        "Chest Depth (cm)",
        min_value=cst.MIN_CHEST_DEPTH,
        max_value=cst.MAX_CHEST_DEPTH,
        value=cst.DEFAULT_CHEST_DEPTH,
        step=1.0,
    )
    height = st.sidebar.slider(
        "Height (cm)",
        min_value=cst.MIN_HEIGHT,
        max_value=cst.MAX_HEIGHT,
        value=cst.DEFAULT_HEIGHT,
        step=1.0,
    )

    # Gender Selection Buttons
    st.sidebar.header("Select Gender")
    if "gender" not in st.session_state:
        st.session_state.gender = "male"  # Default gender

    col1, col2 = st.sidebar.columns(2)
    if col1.button("male"):
        st.session_state.gender = "male"
    if col2.button("female"):
        st.session_state.gender = "female"
    # Display current gender selection
    st.sidebar.write(f"Selected Gender: {st.session_state.gender}")

    current_pedestrian.chest_depth = chest_depth
    current_pedestrian.bideltoid_breadth = bideltoid_breadth
    current_pedestrian.height = height
    current_pedestrian.sex = st.session_state.gender

    # Main Page Content
    st.title("Pedestrian Visualization")
    if st.button("Draw a Pedestrian"):
        fig = plot.display_body3D_orthogonal_projection(current_pedestrian)

        st.pyplot(fig)
        # Save the figure to a BytesIO object in PDF format
        body3D_orthogonal_projection = BytesIO()
        fig.savefig(body3D_orthogonal_projection, format="pdf")
        body3D_orthogonal_projection.seek(0)  # Reset buffer pointer to the beginning

        # Streamlit button in the sidebar to download the graph in PDF format
        st.sidebar.download_button(
            label="Download Image",
            data=body3D_orthogonal_projection,
            file_name="body3D_orthogonal_projection.pdf",
            mime="application/pdf",
        )


def run_tab_pedestrian3D() -> None:
    """
    Execute the main function for the survey tab.

    This function serves as the entry point for running the 2D pedestrian tab
    functionality within the application. It calls the main() function
    to initiate the necessary processes.
    """
    main()
