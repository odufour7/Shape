"""Pedestrian visualization tab."""

import io
import json
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from shapely.geometry import Polygon

import configuration.streamlit_app.utils.constants as cst_app
import configuration.utils.constants as cst
from configuration.models.crowd import Crowd
from configuration.models.measures import CrowdMeasures
from configuration.streamlit_app.plot import plot


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    default_values = {
        "pedestrian_proportion": cst_app.DEFAULT_PEDESTRIAN_PROPORTION,
        "bike_proportion": cst_app.DEFAULT_BIKE_PROPORTION,
        "male_proportion": cst_app.DEFAULT_MALE_PROPORTION,
        "male_chest_depth_mean": cst_app.DEFAULT_MALE_CHEST_DEPTH_MEAN,
        "male_bideltoid_breadth_mean": cst_app.DEFAULT_MALE_BIDELTOID_BREADTH_MEAN,
        "female_chest_depth_mean": cst_app.DEFAULT_FEMALE_CHEST_DEPTH_MEAN,
        "female_bideltoid_breadth_mean": cst_app.DEFAULT_FEMALE_BIDELTOID_BREADTH_MEAN,
        "wheel_width_mean": cst_app.DEFAULT_WHEEL_WIDTH_MEAN,
        "total_length_mean": cst_app.DEFAULT_TOTAL_LENGTH_MEAN,
        "handlebar_length_mean": cst_app.DEFAULT_HANDLEBAR_LENGTH_MEAN,
        "top_tube_length_mean": cst_app.DEFAULT_TOP_TUBE_LENGTH_MEAN,
        "boundary_x": cst_app.DEFAULT_BOUNDARY_X,
        "boundary_y": cst_app.DEFAULT_BOUNDARY_Y,
        "pedestrian_weight": cst_app.DEFAULT_PEDESTRIAN_WEIGHT,
        "bike_weight": cst_app.DEFAULT_BIKE_WEIGHT,
        "repulsion_length": cst_app.DEFAULT_REPULSION_LENGTH_MIN,
        "wall_interaction": cst_app.DEFAULT_WALL_INTERACTION,
        "simulation_run": True,
        "pack_agents": True,
        "desired_direction": cst.DEFAULT_DESIRED_DIRECTION,
        "random_packing": False,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "current_crowd" not in st.session_state:
        initial_boundaries = create_boundaries(cst_app.DEFAULT_BOUNDARY_X, cst_app.DEFAULT_BOUNDARY_Y)
        current_crowd = Crowd(boundaries=initial_boundaries)
        current_crowd.create_agents(cst_app.DEFAULT_AGENT_NUMBER)
        st.session_state.current_crowd = current_crowd
        st.session_state.crowd_measures = current_crowd.measures

    if "num_agents" not in st.session_state:
        st.session_state.num_agents = st.session_state.current_crowd.get_number_agents()


def parameter_changed() -> None:
    """Update the Streamlit session state to indicate that a simulation should be run."""
    st.session_state.simulation_run = True


def create_boundaries(boundary_x: float, boundary_y: float) -> Polygon:
    """
    Create a polygon representing the room boundaries.

    Parameters
    ----------
    boundary_x : float
        Half-width of the room.
    boundary_y : float
        Half-height of the room.

    Returns
    -------
    Polygon
        A polygon object representing the rectangular room boundaries.
    """
    return Polygon(
        [
            (-boundary_x / 2.0, -boundary_y / 2.0),
            (boundary_x / 2.0, -boundary_y / 2.0),
            (boundary_x / 2.0, boundary_y / 2.0),
            (-boundary_x / 2.0, boundary_y / 2.0),
        ]
    )


def update_crowd(boundaries: Polygon, num_agents: int) -> Crowd:
    """
    Create and return a new Crowd object.

    Parameters
    ----------
    boundaries : Polygon
        The boundaries for the simulation area.
    num_agents : int
        The number of agents to create in the crowd.

    Returns
    -------
    Crowd
        A new Crowd object with the specified boundaries and agents.
    """
    crowd = Crowd(boundaries=boundaries)
    crowd.create_agents(num_agents)
    return crowd


def display_interpenetration_warning() -> None:
    """Display a warning if interpenetration is too high."""
    interpenetration_between_agents, interpenetration_with_boundaries = (
        st.session_state.current_crowd.calculate_interpenetration()
    )
    if interpenetration_between_agents > 1e-4:
        st.warning(
            f"The interpenetration area between agents is {interpenetration_between_agents:.2f} cm².\n"
            + "Please rerun or increase the boundaries.",
            icon="⚠️",
        )
    if st.session_state.wall_interaction:
        if interpenetration_with_boundaries > 1e-4:
            st.warning(
                f"The interpenetration area with boundaries is {interpenetration_with_boundaries:.2f} cm².\n"
                + "Please rerun or increase the boundaries.",
                icon="⚠️",
            )


def plot_and_download(current_crowd: Crowd) -> None:
    """
    Plot the crowd and provide download options.

    Parameters
    ----------
    current_crowd : Crowd
        The Crowd object to be plotted and downloaded.
    """
    st.subheader("Visualisation")
    col1, _ = st.columns([1.5, 1])
    with col1:
        fig = plot.display_crowd2D(current_crowd)
        st.pyplot(fig)

        crowd_plot = BytesIO()
        fig.savefig(crowd_plot, format="pdf")
        crowd_plot.seek(0)

        st.sidebar.header("Download")
        st.sidebar.download_button(
            label="Download plot as PDF",
            data=crowd_plot,
            file_name="crowd.pdf",
            mime="application/pdf",
        )

    # Download all files as ZIP
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # check if all agents in the Crowd are pedestrian
    if all(agent.agent_type == cst.AgentTypes.pedestrian for agent in current_crowd.agents):
        filename = f"crowd2D_{timestamp}.zip"

        static_data_bytes, dynamic_data_bytes, geometry_data_bytes, materials_data_bytes = (
            current_crowd.get_all_crowd_params_in_xml()
        )
        # Create an in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("Agents.xml", static_data_bytes)
            zip_file.writestr("AgentDynamics.xml", dynamic_data_bytes)
            zip_file.writestr("Geometry.xml", geometry_data_bytes)
            zip_file.writestr("Materials.xml", materials_data_bytes)

        # Move the buffer's pointer to the beginning
        zip_buffer.seek(0)

        # Add download button for the ZIP file
        st.sidebar.download_button(
            label="Download all files as ZIP",
            data=zip_buffer,
            file_name=filename,
            mime="application/zip",
        )
    else:
        filename = f"crowd2D_{timestamp}.xml"

        data = current_crowd.get_agents_params_in_xml()

        st.sidebar.download_button(
            label="Download as XML",
            data=data,
            file_name=filename,
            mime="application/xml",
        )


def boundaries_state() -> Polygon:
    """
    Create room boundaries and update the session state.

    Returns
    -------
    Polygon
        The new boundaries of the room.
    """
    if st.session_state.wall_interaction:
        boundary_x = st.sidebar.number_input(
            "Length X",
            min_value=cst_app.DEFAULT_BOUNDARY_X_MIN,
            max_value=cst_app.DEFAULT_BOUNDARY_X_MAX,
            value=st.session_state.boundary_x,
            step=1.0,
            on_change=parameter_changed,
        )
        boundary_y = st.sidebar.number_input(
            "Length Y",
            min_value=cst_app.DEFAULT_BOUNDARY_Y_MIN,
            max_value=cst_app.DEFAULT_BOUNDARY_Y_MAX,
            value=st.session_state.boundary_y,
            step=1.0,
            on_change=parameter_changed,
        )
        if boundary_x != st.session_state.boundary_x or boundary_y != st.session_state.boundary_y:
            st.session_state.boundary_x = boundary_x
            st.session_state.boundary_y = boundary_y
            st.session_state.simulation_run = True

        new_boundaries = create_boundaries(st.session_state.boundary_x, st.session_state.boundary_y)
    else:
        new_boundaries = Polygon()

    return new_boundaries


def custom_database_state(new_boundaries: Polygon, num_agents: int) -> None:
    """
    Create custom database and update the session state.

    Parameters
    ----------
    new_boundaries : Polygon
        The new boundaries for the simulation area.
    num_agents : int
        The number of agents in the simulation.
    """
    # Ask to upload a file with the desired dataset
    uploaded_file = st.sidebar.file_uploader("Upload custom dataset", type=["xml"])

    # Provide an example dataset for download
    data_path = Path(__file__).parent.parent.parent.parent / "data"
    xml_path = data_path / "xml" / "custom_crowd_example.xml"
    with open(xml_path, "r", encoding="utf8") as f:
        xml_content = f.read()
    # Sidebar download buttons
    st.sidebar.download_button(
        label="Download XML example dataset", data=xml_content, file_name="custom_crowd_example.xml", mime="application/xml"
    )

    if uploaded_file is not None:
        st.sidebar.success("File successfully uploaded!")

        # Convert uploaded file to dictionary
        uploaded_dict = None
        if uploaded_file.type == "application/json":
            uploaded_dict = json.load(uploaded_file)
            parameter_changed()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
            uploaded_dict = df.to_dict(orient="records")
            parameter_changed()
        st.sidebar.write("Uploaded file converted to dictionary successfully!")

        # Create the Crowd from the dictionary
        if uploaded_dict is not None:
            # uploaded_file should be a dictionary
            if st.session_state.simulation_run:
                crowd_measures = CrowdMeasures(custom_database=uploaded_dict)
                current_crowd = Crowd(boundaries=new_boundaries, measures=crowd_measures)
                current_crowd.create_agents(num_agents)
                st.session_state.current_crowd = current_crowd


def agent_statistics_state(new_boundaries: Polygon, num_agents: int) -> None:
    """
    Create custom statistics and update the session state.

    Parameters
    ----------
    new_boundaries : Polygon
        The new boundaries for the simulation area.
    num_agents : int
        The number of agents in the simulation.
    """
    pedestrian_proportion = st.sidebar.slider(
        "Proportion of pedestrians",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.pedestrian_proportion,
        step=0.1,
        on_change=parameter_changed,
    )
    st.session_state.pedestrian_proportion = pedestrian_proportion
    bike_proportion = 1 - pedestrian_proportion
    st.session_state.bike_proportion = bike_proportion
    if st.session_state.pedestrian_proportion > 0:
        male_proportion = st.sidebar.slider(
            "Proportion of male",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.male_proportion,
            step=0.1,
            on_change=parameter_changed,
        )
        st.session_state.male_proportion = male_proportion
        if st.session_state.male_proportion != 0.0:
            male_chest_depth_mean = st.sidebar.slider(
                "Male mean chest depth",
                min_value=cst_app.DEFAULT_CHEST_DEPTH_MIN,
                max_value=cst_app.DEFAULT_CHEST_DEPTH_MAX,
                value=st.session_state.male_chest_depth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.male_chest_depth_mean = male_chest_depth_mean
            male_bideltoid_breadth_mean = st.sidebar.slider(
                "Male mean bideltoid breadth",
                min_value=cst_app.DEFAULT_BIDELTOID_BREADTH_MIN,
                max_value=cst_app.DEFAULT_BIDELTOID_BREADTH_MAX,
                value=st.session_state.male_bideltoid_breadth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.male_bideltoid_breadth_mean = male_bideltoid_breadth_mean
        if st.session_state.male_proportion != 1.0:
            female_chest_depth_mean = st.sidebar.slider(
                "Female mean chest depth",
                min_value=cst_app.DEFAULT_CHEST_DEPTH_MIN,
                max_value=cst_app.DEFAULT_CHEST_DEPTH_MAX,
                value=st.session_state.female_chest_depth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.female_chest_depth_mean = female_chest_depth_mean
            female_bideltoid_breadth_mean = st.sidebar.slider(
                "Female mean bideltoid breadth",
                min_value=cst_app.DEFAULT_BIDELTOID_BREADTH_MIN,
                max_value=cst_app.DEFAULT_BIDELTOID_BREADTH_MAX,
                value=st.session_state.female_bideltoid_breadth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.female_bideltoid_breadth_mean = female_bideltoid_breadth_mean
    if st.session_state.bike_proportion > 0.0:
        wheel_width_mean = st.sidebar.slider(
            "Wheel width mean",
            min_value=cst_app.DEFAULT_WHEEL_WIDTH_MIN,
            max_value=cst_app.DEFAULT_WHEEL_WIDTH_MAX,
            value=st.session_state.wheel_width_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.wheel_width_mean = wheel_width_mean
        total_length_mean = st.sidebar.slider(
            "Total length mean",
            min_value=cst_app.DEFAULT_TOTAL_LENGTH_MIN,
            max_value=cst_app.DEFAULT_TOTAL_LENGTH_MAX,
            value=st.session_state.total_length_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.total_length_mean = total_length_mean
        handlebar_length_mean = st.sidebar.slider(
            "Handlebar length mean",
            min_value=cst_app.DEFAULT_HANDLEBAR_LENGTH_MIN,
            max_value=cst_app.DEFAULT_HANDLEBAR_LENGTH_MAX,
            value=st.session_state.handlebar_length_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.handlebar_length_mean = handlebar_length_mean
        top_tube_length_mean = st.sidebar.slider(
            "Top tube length mean",
            min_value=cst_app.DEFAULT_TOP_TUBE_LENGTH_MIN,
            max_value=cst_app.DEFAULT_TOP_TUBE_LENGTH_MAX,
            value=st.session_state.top_tube_length_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.top_tube_length_mean = top_tube_length_mean
    agent_statistics = {
        cst.CrowdStat.male_proportion.name: st.session_state.male_proportion,
        cst.CrowdStat.pedestrian_proportion.name: st.session_state.pedestrian_proportion,
        cst.CrowdStat.bike_proportion.name: st.session_state.bike_proportion,
        cst.CrowdStat.male_bideltoid_breadth_mean.name: st.session_state.male_bideltoid_breadth_mean,
        cst.CrowdStat.male_bideltoid_breadth_std_dev.name: cst_app.DEFAULT_MALE_BIDELTOID_BREADTH_STD_DEV,
        cst.CrowdStat.male_bideltoid_breadth_min.name: cst_app.DEFAULT_BIDELTOID_BREADTH_MIN,
        cst.CrowdStat.male_bideltoid_breadth_max.name: cst_app.DEFAULT_BIDELTOID_BREADTH_MAX,
        cst.CrowdStat.male_chest_depth_mean.name: st.session_state.male_chest_depth_mean,
        cst.CrowdStat.male_chest_depth_std_dev.name: cst_app.DEFAULT_MALE_CHEST_DEPTH_STD_DEV,
        cst.CrowdStat.male_chest_depth_min.name: cst_app.DEFAULT_CHEST_DEPTH_MIN,
        cst.CrowdStat.male_chest_depth_max.name: cst_app.DEFAULT_CHEST_DEPTH_MAX,
        cst.CrowdStat.female_bideltoid_breadth_mean.name: st.session_state.female_bideltoid_breadth_mean,
        cst.CrowdStat.female_bideltoid_breadth_std_dev.name: cst_app.DEFAULT_FEMALE_BIDELTOID_BREADTH_STD_DEV,
        cst.CrowdStat.female_bideltoid_breadth_min.name: cst_app.DEFAULT_BIDELTOID_BREADTH_MIN,
        cst.CrowdStat.female_bideltoid_breadth_max.name: cst_app.DEFAULT_BIDELTOID_BREADTH_MAX,
        cst.CrowdStat.female_chest_depth_mean.name: st.session_state.female_chest_depth_mean,
        cst.CrowdStat.female_chest_depth_std_dev.name: cst_app.DEFAULT_FEMALE_CHEST_DEPTH_STD_DEV,
        cst.CrowdStat.female_chest_depth_min.name: cst_app.DEFAULT_CHEST_DEPTH_MIN,
        cst.CrowdStat.female_chest_depth_max.name: cst_app.DEFAULT_CHEST_DEPTH_MAX,
        cst.CrowdStat.wheel_width_mean.name: st.session_state.wheel_width_mean,
        cst.CrowdStat.wheel_width_std_dev.name: cst_app.DEFAULT_WHEEL_WIDTH_STD_DEV,
        cst.CrowdStat.wheel_width_min.name: cst_app.DEFAULT_WHEEL_WIDTH_MIN,
        cst.CrowdStat.wheel_width_max.name: cst_app.DEFAULT_WHEEL_WIDTH_MAX,
        cst.CrowdStat.total_length_mean.name: st.session_state.total_length_mean,
        cst.CrowdStat.total_length_std_dev.name: cst_app.DEFAULT_TOTAL_LENGTH_STD_DEV,
        cst.CrowdStat.total_length_min.name: cst_app.DEFAULT_TOTAL_LENGTH_MIN,
        cst.CrowdStat.total_length_max.name: cst_app.DEFAULT_TOTAL_LENGTH_MAX,
        cst.CrowdStat.handlebar_length_mean.name: st.session_state.handlebar_length_mean,
        cst.CrowdStat.handlebar_length_std_dev.name: cst_app.DEFAULT_HANDLEBAR_LENGTH_STD_DEV,
        cst.CrowdStat.handlebar_length_min.name: cst_app.DEFAULT_HANDLEBAR_LENGTH_MIN,
        cst.CrowdStat.handlebar_length_max.name: cst_app.DEFAULT_HANDLEBAR_LENGTH_MAX,
        cst.CrowdStat.top_tube_length_mean.name: st.session_state.top_tube_length_mean,
        cst.CrowdStat.top_tube_length_std_dev.name: cst_app.DEFAULT_TOP_TUBE_LENGTH_STD_DEV,
        cst.CrowdStat.top_tube_length_min.name: cst_app.DEFAULT_TOP_TUBE_LENGTH_MIN,
        cst.CrowdStat.top_tube_length_max.name: cst_app.DEFAULT_TOP_TUBE_LENGTH_MAX,
        cst.CrowdStat.pedestrian_weight_min.name: cst_app.DEFAULT_PEDESTRIAN_WEIGHT_MIN,
        cst.CrowdStat.pedestrian_weight_max.name: cst_app.DEFAULT_PEDESTRIAN_WEIGHT_MAX,
        cst.CrowdStat.pedestrian_weight_mean.name: cst_app.DEFAULT_PEDESTRIAN_WEIGHT,
        cst.CrowdStat.pedestrian_weight_std_dev.name: cst_app.DEFAULT_PEDESTRIAN_WEIGHT_STD_DEV,
        cst.CrowdStat.bike_weight_min.name: cst_app.DEFAULT_BIKE_WEIGHT_MIN,
        cst.CrowdStat.bike_weight_max.name: cst_app.DEFAULT_BIKE_WEIGHT_MAX,
        cst.CrowdStat.bike_weight_mean.name: cst_app.DEFAULT_BIKE_WEIGHT,
        cst.CrowdStat.bike_weight_std_dev.name: cst_app.DEFAULT_BIKE_WEIGHT_STD_DEV,
    }
    crowd_measures = CrowdMeasures(agent_statistics=agent_statistics)
    # if the measures changed then create a new crowd otherwise do not
    # Check if the measures have changed
    if st.session_state.simulation_run:
        # Update session state if measures have changed
        st.session_state.crowd_measures = crowd_measures

        # Create a new crowd with updated boundaries and measures
        current_crowd = Crowd(boundaries=new_boundaries, measures=crowd_measures)
        current_crowd.create_agents(num_agents)

        # Update the session state with the new crowd
        st.session_state.current_crowd = current_crowd


def general_settings() -> Polygon:
    """
    Configure and return general settings for the simulation.

    Returns
    -------
    Polygon
        The updated boundaries of the simulation area.
    """
    pack_agents: bool = st.sidebar.checkbox("Pack agents", value=True, on_change=parameter_changed)
    if pack_agents != st.session_state.pack_agents:
        st.session_state.pack_agents = pack_agents

    if pack_agents:
        random_packing: bool = st.sidebar.checkbox("Random packing", value=False, on_change=parameter_changed)
        if random_packing != st.session_state.random_packing:
            st.session_state.random_packing = random_packing

        desired_direction = st.sidebar.number_input(
            "Desired direction (degrees)",
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.desired_direction,
            step=1.0,
            on_change=parameter_changed,
        )
        if desired_direction != st.session_state.desired_direction:
            st.session_state.desired_direction = desired_direction

    wall_interaction: bool = st.sidebar.checkbox(
        "Enable wall interaction",
        on_change=parameter_changed,
    )
    if wall_interaction != st.session_state.wall_interaction:
        st.session_state.wall_interaction = wall_interaction

    new_boundaries = boundaries_state()

    num_agents = st.sidebar.number_input(
        "Number of agents",
        min_value=cst_app.DEFAULT_AGENT_NUMBER_MIN,
        max_value=cst_app.DEFAULT_AGENT_NUMBER_MAX,
        value=st.session_state.num_agents,
        step=1,
        on_change=parameter_changed,
    )

    if num_agents != st.session_state.num_agents:
        st.session_state.num_agents = num_agents

    repulsion_length: float = st.sidebar.slider(
        "Repulsion length",
        min_value=cst_app.DEFAULT_REPULSION_LENGTH_MIN,
        max_value=cst_app.DEFAULT_REPULSION_LENGTH_MAX,
        value=cst.DEFAULT_REPULSION_LENGTH,
        step=0.01,
        on_change=parameter_changed,
    )
    if repulsion_length != st.session_state.repulsion_length:
        st.session_state.repulsion_length = repulsion_length

    return new_boundaries


def run_tab_crowd() -> None:
    """
    Provide an interactive interface for simulating and visualizing a crowd of agents.

    Users can configure general settings, select databases, and control agent packing behavior.
    The tab includes options for crowd visualization and downloading results.

    Attributes
    ----------
    Sidebar:
        - General settings:
            - Toggle for packing agents.
            - Input fields for boundaries, number of agents, wall interaction strength, and repulsion length.
        - Database selection:
            - Options: ANSURII database, Custom database, Custom statistics.
            - Additional settings for custom databases/statistics.
        - Download options:
            - Export results as files.

    Main Page:
        - Crowd visualization using Plotly charts.
        - Interpenetration warnings if applicable.

    Notes
    -----
    - Three database options are available:
        - ANSURII database.
        - Custom statistics.
    - If agent packing is enabled, agents are packed using force-based interactions.
      Otherwise, the crowd is unpacked.
    - Interpenetration between agents is calculated and displayed as a warning if necessary.
    """
    st.info(
        "The computation of the random packing of the crowd is ongoing and may take some time. Please be patient.",
        icon="⏳",
    )

    initialize_session_state()

    st.sidebar.header("General settings")

    new_boundaries = general_settings()

    # Rolling menu to select between ANSURII database / custom Database / Custom Statistics
    database_option = st.sidebar.selectbox(
        "Select database option:",
        options=["ANSURII database", "Custom statistics"],  # "Custom database"
    )
    if "database_option" not in st.session_state:
        st.session_state.database_option = database_option

    if database_option == "ANSURII database":
        if st.session_state.simulation_run:
            current_crowd = Crowd(boundaries=new_boundaries)
            current_crowd.create_agents(st.session_state.num_agents)
            st.session_state.current_crowd = current_crowd

    # elif database_option == "Custom database":
    #     st.sidebar.header(f"{database_option} settings")
    #     custom_database_state(new_boundaries, st.session_state.num_agents)

    else:  # Custom Statistics
        st.sidebar.header(f"{database_option} settings")
        agent_statistics_state(new_boundaries, st.session_state.num_agents)

    if st.session_state.pack_agents:
        if st.session_state.simulation_run:
            # unpacked_agents = st.session_state.current_crowd.get_agents_params()

            st.session_state.current_crowd.pack_agents_with_forces(
                st.session_state.repulsion_length, st.session_state.desired_direction, st.session_state.random_packing
            )
            st.session_state.simulation_run = False
    else:
        st.session_state.current_crowd.unpack_crowd()

    if st.session_state.pack_agents:
        display_interpenetration_warning()

    plot_and_download(st.session_state.current_crowd)
