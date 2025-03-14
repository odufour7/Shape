"""Pedestrian Visualization Tab."""

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from shapely.geometry import Polygon

import src.shapes_package.utils.constants as cst
from src.shapes_package.classes.crowd import Crowd
from src.shapes_package.classes.measures import CrowdMeasures
from src.shapes_package.plotting import plot
from src.shapes_package.utils import functions as fun
from src.shapes_package.utils.typing_custom import BackupDataType


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    default_values = {
        "pedestrian_proportion": cst.DEFAULT_PEDESTRIAN_PROPORTION,
        "bike_proportion": cst.DEFAULT_BIKE_PROPORTION,
        "male_proportion": cst.DEFAULT_MALE_PROPORTION,
        "male_chest_depth_mean": cst.DEFAULT_MALE_CHEST_DEPTH_MEAN,
        "male_bideltoid_breadth_mean": cst.DEFAULT_MALE_BIDELTOID_BREADTH_MEAN,
        "female_chest_depth_mean": cst.DEFAULT_FEMALE_CHEST_DEPTH_MEAN,
        "female_bideltoid_breadth_mean": cst.DEFAULT_FEMALE_BIDELTOID_BREADTH_MEAN,
        "wheel_width_mean": cst.DEFAULT_WHEEL_WIDTH_MEAN,
        "total_length_mean": cst.DEFAULT_TOTAL_LENGTH_MEAN,
        "handlebar_length_mean": cst.DEFAULT_HANDLEBAR_LENGTH_MEAN,
        "top_tube_length_mean": cst.DEFAULT_TOP_TUBE_LENGTH_MEAN,
        "boundary_x": cst.DEFAULT_BOUNDARY_X,
        "boundary_y": cst.DEFAULT_BOUNDARY_Y,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "current_crowd" not in st.session_state:
        initial_boundaries = create_boundaries(cst.DEFAULT_BOUNDARY_X, cst.DEFAULT_BOUNDARY_Y)
        current_crowd = Crowd(boundaries=initial_boundaries)
        current_crowd.create_agents(cst.DEFAULT_AGENT_NUMBER)
        st.session_state.current_crowd = current_crowd
        st.session_state.crowd_measures = current_crowd.measures

    if "num_agents" not in st.session_state:
        st.session_state.num_agents = st.session_state.current_crowd.get_number_agents()


def create_boundaries(boundary_x: float, boundary_y: float) -> Polygon:
    """Create a polygon representing the room boundaries."""
    return Polygon(
        [
            (-boundary_x, -boundary_y),
            (boundary_x, -boundary_y),
            (boundary_x, boundary_y),
            (-boundary_x, boundary_y),
        ]
    )


def update_crowd(boundaries: Polygon, num_agents: int) -> Crowd:
    """Create and return a new Crowd object."""
    crowd = Crowd(boundaries=boundaries)
    crowd.create_agents(num_agents)
    return crowd


def display_interpenetration_warning(interpenetration: float) -> None:
    """Display a warning if interpenetration is too high."""
    if interpenetration > 1e-4:
        st.warning(
            f"The interpenetration area is {interpenetration:.2f} cm².\nPlease rerun or increase the boundaries.",
            icon="⚠️",
        )


def plot_and_download(current_crowd: Crowd) -> None:
    """Plot the crowd and provide download option."""
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
    # Create a select box for format selection
    backup_data_type: BackupDataType = st.sidebar.selectbox(
        "Select backup format:",
        options=[cst.BackupDataTypes.json.name, cst.BackupDataTypes.xml.name],
        format_func=lambda x: x.upper(),
        help="Choose the format for your data backup.",
    )
    # Add a download button
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crowd2D_{backup_data_type}_{timestamp}.{backup_data_type}"
    data, mime_type = fun.get_shapes_data(backup_data_type, current_crowd.get_agents_params())
    st.sidebar.download_button(
        label=f"Download data as {backup_data_type.upper()}",
        data=data,
        file_name=filename,
        mime=mime_type,
    )


def boundaries_state() -> Polygon:
    """Create the boundaries of the room and update the session state."""
    boundary_x = st.sidebar.number_input(
        "Boundary X",
        min_value=cst.DEFAULT_BOUNDARY_X_MIN,
        max_value=cst.DEFAULT_BOUNDARY_X_MAX,
        value=st.session_state.boundary_x,
        step=1.0,
    )
    boundary_y = st.sidebar.number_input(
        "Boundary Y",
        min_value=cst.DEFAULT_BOUNDARY_Y_MIN,
        max_value=cst.DEFAULT_BOUNDARY_Y_MAX,
        value=st.session_state.boundary_y,
        step=1.0,
    )
    if boundary_x != st.session_state.boundary_x:
        st.session_state.boundary_x = boundary_x
    if boundary_y != st.session_state.boundary_y:
        st.session_state.boundary_y = boundary_y

    new_boundaries = create_boundaries(st.session_state.boundary_x, st.session_state.boundary_y)
    return new_boundaries


def custom_database_state(new_boundaries: Polygon, num_agents: int) -> None:
    """Create the custom database and update the session state."""
    # Ask to upload a file with the desired dataset
    uploaded_file = st.sidebar.file_uploader("Upload custom dataset", type=["json", "xlm"])
    # Provide an example dataset for download
    path_file = Path(__file__).parent.parent.parent.parent / "data" / "json"
    with open(path_file / "custom_crowd_example.json", "r", encoding="utf8") as f:
        st.sidebar.download_button(
            label="Download example dataset", data=f.read(), file_name="custom_crowd_example.json", mime="application/json"
        )

    if uploaded_file is not None:
        st.sidebar.success("File successfully uploaded!")
        # Convert uploaded file to dictionary
        uploaded_dict = None
        if uploaded_file.type == "application/json":
            uploaded_dict = json.load(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
            uploaded_dict = df.to_dict(orient="records")
        st.sidebar.write("Uploaded file converted to dictionary successfully!")
        if uploaded_dict is not None:
            # uploaded_file should be a dictionary
            crowd_measures = CrowdMeasures(custom_database=uploaded_dict)
            current_crowd = Crowd(boundaries=new_boundaries, measures=crowd_measures)
            current_crowd.create_agents(num_agents)
            st.session_state.current_crowd = current_crowd


def agent_statistics_state(new_boundaries: Polygon, num_agents: int) -> None:
    """Create the custom statistics and update the session state."""
    pedestrian_proportion = st.sidebar.slider(
        "Proportion of pedestrians",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.pedestrian_proportion,
        step=0.1,
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
        )
        st.session_state.male_proportion = male_proportion
        if st.session_state.male_proportion != 0.0:
            male_chest_depth_mean = st.sidebar.slider(
                "Male mean chest depth",
                min_value=cst.DEFAULT_CHEST_DEPTH_MIN,
                max_value=cst.DEFAULT_CHEST_DEPTH_MAX,
                value=st.session_state.male_chest_depth_mean,
                step=1.0,
            )
            st.session_state.male_chest_depth_mean = male_chest_depth_mean
            male_bideltoid_breadth_mean = st.sidebar.slider(
                "Male mean bideltoid breadth",
                min_value=cst.DEFAULT_BIDELTOID_BREADTH_MIN,
                max_value=cst.DEFAULT_BIDELTOID_BREADTH_MAX,
                value=st.session_state.male_bideltoid_breadth_mean,
                step=1.0,
            )
            st.session_state.male_bideltoid_breadth_mean = male_bideltoid_breadth_mean
        if st.session_state.male_proportion != 1.0:
            female_chest_depth_mean = st.sidebar.slider(
                "Female mean chest depth",
                min_value=cst.DEFAULT_CHEST_DEPTH_MIN,
                max_value=cst.DEFAULT_CHEST_DEPTH_MAX,
                value=st.session_state.female_chest_depth_mean,
                step=1.0,
            )
            st.session_state.female_chest_depth_mean = female_chest_depth_mean
            female_bideltoid_breadth_mean = st.sidebar.slider(
                "Female mean bideltoid breadth",
                min_value=cst.DEFAULT_BIDELTOID_BREADTH_MIN,
                max_value=cst.DEFAULT_BIDELTOID_BREADTH_MAX,
                value=st.session_state.female_bideltoid_breadth_mean,
                step=1.0,
            )
            st.session_state.female_bideltoid_breadth_mean = female_bideltoid_breadth_mean
    if st.session_state.bike_proportion > 0.0:
        wheel_width_mean = st.sidebar.slider(
            "Wheel width mean",
            min_value=cst.DEFAULT_WHEEL_WIDTH_MIN,
            max_value=cst.DEFAULT_WHEEL_WIDTH_MAX,
            value=st.session_state.wheel_width_mean,
            step=1.0,
        )
        st.session_state.wheel_width_mean = wheel_width_mean
        total_length_mean = st.sidebar.slider(
            "Total length mean",
            min_value=cst.DEFAULT_TOTAL_LENGTH_MIN,
            max_value=cst.DEFAULT_TOTAL_LENGTH_MAX,
            value=st.session_state.total_length_mean,
            step=1.0,
        )
        st.session_state.total_length_mean = total_length_mean
        handlebar_length_mean = st.sidebar.slider(
            "Handlebar length mean",
            min_value=cst.DEFAULT_HANDLEBAR_LENGTH_MIN,
            max_value=cst.DEFAULT_HANDLEBAR_LENGTH_MAX,
            value=st.session_state.handlebar_length_mean,
            step=1.0,
        )
        st.session_state.handlebar_length_mean = handlebar_length_mean
        top_tube_length_mean = st.sidebar.slider(
            "Top tube length mean",
            min_value=cst.DEFAULT_TOP_TUBE_LENGTH_MIN,
            max_value=cst.DEFAULT_TOP_TUBE_LENGTH_MAX,
            value=st.session_state.top_tube_length_mean,
            step=1.0,
        )
        st.session_state.top_tube_length_mean = top_tube_length_mean
    agent_statistics = {
        cst.CrowdStat.male_proportion.name: st.session_state.male_proportion,
        cst.CrowdStat.pedestrian_proportion.name: st.session_state.pedestrian_proportion,
        cst.CrowdStat.bike_proportion.name: st.session_state.bike_proportion,
        cst.CrowdStat.male_bideltoid_breadth_mean.name: st.session_state.male_bideltoid_breadth_mean,
        cst.CrowdStat.male_bideltoid_breadth_std_dev.name: cst.DEFAULT_MALE_BIDELTOID_BREADTH_STD_DEV,
        cst.CrowdStat.male_bideltoid_breadth_min.name: cst.DEFAULT_BIDELTOID_BREADTH_MIN,
        cst.CrowdStat.male_bideltoid_breadth_max.name: cst.DEFAULT_BIDELTOID_BREADTH_MAX,
        cst.CrowdStat.male_chest_depth_mean.name: st.session_state.male_chest_depth_mean,
        cst.CrowdStat.male_chest_depth_std_dev.name: cst.DEFAULT_MALE_CHEST_DEPTH_STD_DEV,
        cst.CrowdStat.male_chest_depth_min.name: cst.DEFAULT_CHEST_DEPTH_MIN,
        cst.CrowdStat.male_chest_depth_max.name: cst.DEFAULT_CHEST_DEPTH_MAX,
        cst.CrowdStat.female_bideltoid_breadth_mean.name: st.session_state.female_bideltoid_breadth_mean,
        cst.CrowdStat.female_bideltoid_breadth_std_dev.name: cst.DEFAULT_FEMALE_BIDELTOID_BREADTH_STD_DEV,
        cst.CrowdStat.female_bideltoid_breadth_min.name: cst.DEFAULT_BIDELTOID_BREADTH_MIN,
        cst.CrowdStat.female_bideltoid_breadth_max.name: cst.DEFAULT_BIDELTOID_BREADTH_MAX,
        cst.CrowdStat.female_chest_depth_mean.name: st.session_state.female_chest_depth_mean,
        cst.CrowdStat.female_chest_depth_std_dev.name: cst.DEFAULT_FEMALE_CHEST_DEPTH_STD_DEV,
        cst.CrowdStat.female_chest_depth_min.name: cst.DEFAULT_CHEST_DEPTH_MIN,
        cst.CrowdStat.female_chest_depth_max.name: cst.DEFAULT_CHEST_DEPTH_MAX,
        cst.CrowdStat.wheel_width_mean.name: st.session_state.wheel_width_mean,
        cst.CrowdStat.wheel_width_std_dev.name: cst.DEFAULT_WHEEL_WIDTH_STD_DEV,
        cst.CrowdStat.wheel_width_min.name: cst.DEFAULT_WHEEL_WIDTH_MIN,
        cst.CrowdStat.wheel_width_max.name: cst.DEFAULT_WHEEL_WIDTH_MAX,
        cst.CrowdStat.total_length_mean.name: st.session_state.total_length_mean,
        cst.CrowdStat.total_length_std_dev.name: cst.DEFAULT_TOTAL_LENGTH_STD_DEV,
        cst.CrowdStat.total_length_min.name: cst.DEFAULT_TOTAL_LENGTH_MIN,
        cst.CrowdStat.total_length_max.name: cst.DEFAULT_TOTAL_LENGTH_MAX,
        cst.CrowdStat.handlebar_length_mean.name: st.session_state.handlebar_length_mean,
        cst.CrowdStat.handlebar_length_std_dev.name: cst.DEFAULT_HANDLEBAR_LENGTH_STD_DEV,
        cst.CrowdStat.handlebar_length_min.name: cst.DEFAULT_HANDLEBAR_LENGTH_MIN,
        cst.CrowdStat.handlebar_length_max.name: cst.DEFAULT_HANDLEBAR_LENGTH_MAX,
        cst.CrowdStat.top_tube_length_mean.name: st.session_state.top_tube_length_mean,
        cst.CrowdStat.top_tube_length_std_dev.name: cst.DEFAULT_TOP_TUBE_LENGTH_STD_DEV,
        cst.CrowdStat.top_tube_length_min.name: cst.DEFAULT_TOP_TUBE_LENGTH_MIN,
        cst.CrowdStat.top_tube_length_max.name: cst.DEFAULT_TOP_TUBE_LENGTH_MAX,
    }
    crowd_measures = CrowdMeasures(agent_statistics=agent_statistics)
    # if the measures changed then create a new crowd otherwise do not
    # Check if the measures have changed
    if st.session_state.crowd_measures != crowd_measures:  # doesn't work well
        # Update session state if measures have changed
        st.session_state.crowd_measures = crowd_measures

        # Create a new crowd with updated boundaries and measures
        current_crowd = Crowd(boundaries=new_boundaries, measures=crowd_measures)
        current_crowd.create_agents(num_agents)

        # Update the session state with the new crowd
        st.session_state.current_crowd = current_crowd

    # current_crowd = Crowd(boundaries=new_boundaries, measures=crowd_measures)
    # current_crowd.create_agents(num_agents)
    # st.session_state.current_crowd = current_crowd


def main() -> None:
    """Run the main function for the crowd tab."""
    st.info(
        "The computation of the random packing of the crowd is ongoing and may take some time. Please be patient.",
        icon="⏳",
    )

    initialize_session_state()

    st.sidebar.header("General settings")
    # Rolling menu to select between ANSURII database / custom Database / Custom Statistics
    database_option = st.sidebar.selectbox(
        "Select database option:", options=["ANSURII database", "Custom database", "Custom statistics"]
    )
    if "database_option" not in st.session_state:
        st.session_state.database_option = database_option

    new_boundaries = boundaries_state()

    num_agents = st.sidebar.number_input(
        "Number of agents",
        min_value=cst.DEFAULT_AGENT_NUMBER_MIN,
        max_value=cst.DEFAULT_AGENT_NUMBER_MAX,
        value=st.session_state.num_agents,
        step=1,
    )

    if num_agents != st.session_state.num_agents:
        st.session_state.num_agents = num_agents

    if database_option == "ANSURII database":
        current_crowd = Crowd(boundaries=new_boundaries)

        current_crowd.create_agents(num_agents)

        st.session_state.current_crowd = current_crowd

    elif database_option == "Custom database":
        st.sidebar.header(f"{database_option} settings")
        custom_database_state(new_boundaries, num_agents)

    else:  # Custom Statistics
        st.sidebar.header(f"{database_option} settings")
        # set the default values for the statistics
        agent_statistics_state(new_boundaries, num_agents)

    st.session_state.current_crowd.pack_agents_with_forces()

    interpenetration = st.session_state.current_crowd.calculate_interpenetration()
    display_interpenetration_warning(interpenetration)

    plot_and_download(st.session_state.current_crowd)


def run_tab_crowd() -> None:
    """Run the crowd tab by invoking the main function.

    This function is responsible for initializing and displaying the crowd tab
    within the application. It calls the main function to perform the necessary
    operations to set up and run the tab.

    Returns
    -------
        None
    """
    main()
