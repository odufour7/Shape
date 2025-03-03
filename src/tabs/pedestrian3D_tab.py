"""3D Pedestrian Visualization Tab"""

from datetime import datetime
from io import BytesIO

import streamlit as st

import src.utils.constants as cst
from src.classes.agents import Agent
from src.classes.measures import AgentMeasures
from src.plotting import plot
from src.utils import functions as fun


def main() -> None:
    """Main function for the 3D pedestrian tab."""
    # Initialize the object only if it doesn't exist
    if "current_pedestrian" not in st.session_state:
        # Create a new pedestrian object
        pedestrian_measures = AgentMeasures(
            agent_type="pedestrian",
            measures={
                "sex": cst.DEFAULT_SEX,
                "bideltoid_breadth": cst.DEFAULT_BIDELTOID_BREADTH,
                "chest_depth": cst.DEFAULT_CHEST_DEPTH,
                "height": cst.DEFAULT_HEIGHT,
            },
        )
        st.session_state.current_pedestrian = Agent(agent_type="pedestrian", measures=pedestrian_measures)

    # Access the stored object
    current_pedestrian = st.session_state.current_pedestrian

    # Sidebar Sliders for Anthropometric Parameters
    st.sidebar.header("Adjust parameters")

    # Sex Selection
    sex_options = ["male", "female"]
    st.sidebar.radio(
        "Select the pedestrian's sex:",
        options=sex_options,
        index=0,  # Default to "male"
        key="sex",  # Automatically syncs with st.session_state["sex"]
    )

    bideltoid_breadth = st.sidebar.slider(
        "Bideltoid breadth (cm)",
        min_value=cst.MIN_BIDELTOID_BREADTH,
        max_value=cst.MAX_BIDELTOID_BREADTH,
        value=cst.DEFAULT_BIDELTOID_BREADTH,
        step=1.0,
    )
    chest_depth = st.sidebar.slider(
        "Chest depth (cm)",
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
    pedestrian_measures = AgentMeasures(
        agent_type="pedestrian",
        measures={
            "sex": st.session_state.sex,
            "bideltoid_breadth": bideltoid_breadth,
            "chest_depth": chest_depth,
            "height": height,
        },
    )
    current_pedestrian.measures = pedestrian_measures

    # Main Page Content
    st.subheader("Visualisation")
    # Sidebar menu for selecting visualization type
    menu_option = st.selectbox(
        "Choose an option:",
        [
            "Display orthogonal projection",
            "Display the body in 3D as a superposition of slices",
            "Display the body in 3D with a mesh",
        ],
    )

    if menu_option != "Display orthogonal projection":
        # Input fields for translation and rotation
        x_translation = st.sidebar.number_input("X-translation (cm):", min_value=-500.0, max_value=500.0, value=0.0, step=1.0)
        y_translation = st.sidebar.number_input("Y-translation (cm):", min_value=-500.0, max_value=500.0, value=0.0, step=1.0)
        rotation_angle = st.sidebar.number_input(
            "Rotation angle around z-axis (degrees):", min_value=-360.0, max_value=360.0, value=0.0, step=1.0
        )

        current_pedestrian.translate_body3D(x_translation, y_translation, dz=0.0)
        current_pedestrian.rotate_body3D(rotation_angle)

    col1, _ = st.columns([2.0, 1])  # Adjust proportions as needed
    with col1:
        # Display content based on the selected menu option
        if menu_option == "Display orthogonal projection":

            title_progress_bar = st.text("Progress bar")
            my_progress_bar = st.progress(0)
            status_text = st.empty()

            # Compute the orthogonal projection
            fig = plot.display_body3D_orthogonal_projection(current_pedestrian, extra_info=[my_progress_bar, status_text])
            # Display the figure
            st.pyplot(fig)

            status_text.text("Operation complete! ⌛")
            my_progress_bar.empty()
            title_progress_bar.empty()
            status_text.empty()

            # Save the figure to a BytesIO object in PDF format
            body3D_orthogonal_projection = BytesIO()
            fig.savefig(body3D_orthogonal_projection, format="pdf")
            body3D_orthogonal_projection.seek(0)  # Reset buffer pointer to the beginning

            # Streamlit button in the sidebar to download the graph in PDF format
            st.sidebar.header("Download")
            st.sidebar.download_button(
                label="Download orthogonal projection as PDF",
                data=body3D_orthogonal_projection,
                file_name="body3D_orthogonal_projection.pdf",
                mime="application/pdf",
            )

        elif menu_option == "Display the body in 3D as a superposition of slices":

            title_progress_bar = st.text("Progress Bar")
            my_progress_bar = st.progress(0)
            status_text = st.empty()

            # Compute the 3D body with slices
            fig = plot.display_body3D_polygons(current_pedestrian, extra_info=[my_progress_bar, status_text])
            # Display the figure
            st.plotly_chart(fig)

            status_text.text("Operation complete! ⌛")
            my_progress_bar.empty()
            title_progress_bar.empty()
            status_text.empty()

            # Streamlit button in the sidebar to download the graph in PDF format
            st.sidebar.header("Download")
            st.sidebar.download_button(
                label="Download the 3D body with slices as PDF",
                data=fig.to_image(format="pdf"),
                file_name="body3D_slices.pdf",
            )

        elif menu_option == "Display the body in 3D with a mesh":

            precision = st.sidebar.slider(
                "Precision of the mesh",
                min_value=1,
                max_value=60,
                value=40,
                step=1,
            )

            title_progress_bar = st.text("Progress Bar")
            my_progress_bar = st.progress(0)
            status_text = st.empty()

            # Compute the 3D body with a mesh
            fig = plot.display_body3D_mesh(current_pedestrian, extra_info=[my_progress_bar, status_text, precision])
            # Display the figure
            st.plotly_chart(fig)

            status_text.text("Operation complete! ⌛")
            my_progress_bar.empty()
            title_progress_bar.empty()
            status_text.empty()

            # Streamlit button in the sidebar to download the graph in PDF format
            st.sidebar.header("Download")
            st.sidebar.download_button(
                label="Download the 3D body with a mesh as PDF",
                data=fig.to_image(format="pdf"),
                file_name="body3D_mesh.pdf",
            )

    # Add a download button
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"agent3D_{current_pedestrian.agent_type}_{current_pedestrian.measures.measures["sex"]}_{timestamp}.pkl"
    data_to_download, mime_type = fun.get_shapes_data("pickle", current_pedestrian.shapes3D.shapes)
    st.sidebar.download_button(
        label="Download data as PKL",
        data=data_to_download,
        file_name=filename,
        mime=mime_type,
    )


def run_tab_pedestrian3D() -> None:
    """
    Execute the main function for the 3D pedestrian tab.
    """
    main()
