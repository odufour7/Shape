"""3D pedestrian visualization tab."""

import pickle
from datetime import datetime
from io import BytesIO

import plotly.graph_objects as go
import streamlit as st
from matplotlib.figure import Figure

import configuration.utils.constants as cst
import streamlit_app.utils.constants as cst_app
from configuration.models.agents import Agent
from configuration.models.initial_agents import InitialPedestrian
from configuration.models.measures import AgentMeasures
from streamlit_app.plot import plot


def initialize_session_state() -> None:
    """Initialize the session state for the pedestrian tab."""
    if "current_pedestrian" not in st.session_state:
        initial_pedestrian = InitialPedestrian(cst_app.DEFAULT_SEX)
        # Create a new pedestrian object
        pedestrian_measures = AgentMeasures(
            agent_type=cst.AgentTypes.pedestrian,
            measures={
                "sex": cst_app.DEFAULT_SEX,
                "bideltoid_breadth": initial_pedestrian.measures[cst.PedestrianParts.bideltoid_breadth.name],
                "chest_depth": initial_pedestrian.measures[cst.PedestrianParts.chest_depth.name],
                "height": initial_pedestrian.measures[cst.PedestrianParts.height.name],
                "weight": initial_pedestrian.measures[cst.CommonMeasures.weight.name],
            },
        )
        st.session_state.current_pedestrian = Agent(agent_type=cst.AgentTypes.pedestrian, measures=pedestrian_measures)


def sliders_for_agent_parameters() -> AgentMeasures:
    """
    Create sliders in the sidebar for adjusting pedestrian parameters.

    Attributes
    ----------
    Sidebar:
        - Radio button for selecting sex (male or female).
        - Sliders for anthropometric parameters:
            - Bideltoid breadth (cm).
            - Chest depth (cm).
            - Height (cm).

    Returns
    -------
    AgentMeasures
        An object containing the updated measures for the pedestrian agent, including sex,
        bideltoid breadth, chest depth, height, and weight.
    """
    # Sex Selection
    st.sidebar.radio(
        "Select the pedestrian's sex:",
        options=["male", "female"],
        index=0,  # Default to "male"
        key="sex",  # Automatically syncs with st.session_state.sex
    )
    initial_pedestrian = InitialPedestrian(st.session_state.sex)

    # Sliders for anthropometric parameters
    bideltoid_breadth: float = st.sidebar.slider(
        "Bideltoid breadth (cm)",
        min_value=cst.CrowdStat["male_bideltoid_breadth_min"],
        max_value=cst.CrowdStat["male_bideltoid_breadth_max"],
        value=float(initial_pedestrian.measures[cst.PedestrianParts.bideltoid_breadth.name]),
        step=1.0,
    )
    chest_depth: float = st.sidebar.slider(
        "Chest depth (cm)",
        min_value=cst.CrowdStat["male_chest_depth_min"],
        max_value=cst.CrowdStat["male_chest_depth_max"],
        value=float(initial_pedestrian.measures[cst.PedestrianParts.chest_depth.name]),
        step=1.0,
    )
    height: float = st.sidebar.slider(
        "Height (cm)",
        min_value=float(cst_app.DEFAULT_HEIGHT_MIN),
        max_value=float(cst_app.DEFAULT_HEIGHT_MAX),
        value=float(initial_pedestrian.measures[cst.PedestrianParts.height.name]),
        step=1.0,
    )

    # Create the AgentMeasures object with the updated values
    pedestrian_measures = AgentMeasures(
        agent_type=cst.AgentTypes.pedestrian,
        measures={
            "sex": st.session_state.sex,
            "bideltoid_breadth": bideltoid_breadth,
            "chest_depth": chest_depth,
            "height": height,
            "weight": initial_pedestrian.measures[cst.CommonMeasures.weight.name],
        },
    )
    return pedestrian_measures


def sliders_for_agent_position() -> tuple[float, float, float]:
    """
    Create input fields in the sidebar for adjusting an agent's position and rotation.

    Returns
    -------
    tuple[float, float, float]
        A tuple containing:
        - `x_translation` (float): The translation along the X-axis in centimeters.
        - `y_translation` (float): The translation along the Y-axis in centimeters.
        - `rotation_angle` (float): The rotation angle around the Z-axis in degrees.
    """
    x_translation = st.sidebar.number_input(
        "X-translation (cm):",
        min_value=-500.0,
        max_value=500.0,
        value=0.0,
        step=1.0,
    )
    y_translation = st.sidebar.number_input(
        "Y-translation (cm):",
        min_value=-500.0,
        max_value=500.0,
        value=0.0,
        step=1.0,
    )
    rotation_angle = st.sidebar.number_input(
        "Rotation angle around z-axis (degrees):",
        min_value=-360.0,
        max_value=360.0,
        value=0.0,
        step=1.0,
    )
    return x_translation, y_translation, rotation_angle


def download_data(current_pedestrian: Agent) -> None:
    """
    Provide a download button in the sidebar to export the agent's data as a pickle file.

    Parameters
    ----------
    current_pedestrian : Agent
        The agent object representing the current pedestrian. It contains the 3D shape
        data (`shapes3D`) and anthropometric measures (`measures`) to be exported.

    Notes
    -----
    - The filename is dynamically generated using the agent type, sex, and a timestamp in the format `YYYYMMDD_HHMMSS`.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"agent3D_{current_pedestrian.agent_type}_{current_pedestrian.measures.measures['sex']}_{timestamp}.pkl"
    data_to_download = pickle.dumps(current_pedestrian.shapes3D.shapes)
    st.sidebar.download_button(
        label="Download data as PKL",
        data=data_to_download,
        file_name=filename,
        mime="application/octet-stream",
    )


def run_tab_pedestrian3D() -> None:
    """
    Provide an interactive interface for visualizing and interacting with a 3D representation of a pedestrian agent.

    Users can adjust anthropometric parameters, manipulate position and rotation, and choose from different visualization
    modes. Download options for figures and data are also provided.

    Main Page:
        - Visualization of the selected 3D representation mode:
            - Orthogonal projection (matplotlib figure).
            - 3D body as slices (Plotly figure).
            - 3D body with a mesh (Plotly figure).
        - Progress bars and status messages during computations.
    """
    initialize_session_state()
    current_pedestrian = st.session_state.current_pedestrian

    # Sidebar Sliders for Anthropometric Parameters
    st.sidebar.header("Adjust parameters")
    pedestrian_measures = sliders_for_agent_parameters()
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
        x_translation, y_translation, rotation_angle = sliders_for_agent_position()
        current_pedestrian.translate_body3D(x_translation, y_translation, dz=0.0)
        current_pedestrian.rotate_body3D(rotation_angle)

    col1, _ = st.columns([2.0, 1])
    with col1:
        # Display content based on the selected menu option
        if menu_option == "Display orthogonal projection":
            title_progress_bar = st.text("Progress bar")
            my_progress_bar = st.progress(0)
            status_text = st.empty()

            # Compute the orthogonal projection
            fig: Figure = plot.display_body3D_orthogonal_projection(current_pedestrian, extra_info=(my_progress_bar, status_text))
            # Display the figure
            st.pyplot(fig)

            status_text.text("Operation complete! ⌛")
            my_progress_bar.empty()
            title_progress_bar.empty()
            status_text.empty()

            # Save the figure to a BytesIO object in PDF format
            body3D_orthogonal_projection = BytesIO()
            fig.savefig(body3D_orthogonal_projection, format="pdf")
            body3D_orthogonal_projection.seek(0)

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
            fig_plotly: go.Figure = plot.display_body3D_polygons(current_pedestrian, extra_info=(my_progress_bar, status_text))
            # Display the figure
            st.plotly_chart(fig_plotly)

            status_text.text("Operation complete! ⌛")
            my_progress_bar.empty()
            title_progress_bar.empty()
            status_text.empty()

            # Streamlit button in the sidebar to download the graph in PDF format
            st.sidebar.header("Download")
            st.sidebar.download_button(
                label="Download the 3D body with slices as PDF",
                data=fig_plotly.to_image(format="pdf"),
                file_name="body3D_slices.pdf",
            )

        elif menu_option == "Display the body in 3D with a mesh":
            precision = st.sidebar.slider(
                "Precision of the mesh (number of slices plotted)",
                min_value=10,
                max_value=len(current_pedestrian.shapes3D.shapes.keys()),
                value=20,
                step=1,
            )

            title_progress_bar = st.text("Progress Bar")
            my_progress_bar = st.progress(0)
            status_text = st.empty()

            # Compute the 3D body with a mesh
            fig_plotly_mesh: go.Figure = plot.display_body3D_mesh(
                current_pedestrian, precision, extra_info=(my_progress_bar, status_text)
            )

            # Display the figure
            st.plotly_chart(fig_plotly_mesh)

            status_text.text("Operation complete! ⌛")
            my_progress_bar.empty()
            title_progress_bar.empty()
            status_text.empty()

            # Streamlit button in the sidebar to download the graph in PDF format
            st.sidebar.header("Download")
            st.sidebar.download_button(
                label="Download the 3D body with a mesh as PDF",
                data=fig_plotly_mesh.to_image(format="pdf"),
                file_name="body3D_mesh.pdf",
            )

    # Download data button
    download_data(current_pedestrian)
