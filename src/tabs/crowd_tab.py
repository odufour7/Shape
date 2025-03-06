"""Pedestrian Visualization Tab"""

from datetime import datetime
from io import BytesIO

import streamlit as st
from shapely.geometry import Polygon

import src.utils.constants as cst
from src.classes.crowd import Crowd
from src.plotting import plot
from src.utils import functions as fun


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


def display_interpenetration_warning(interpenetration: float):
    """Display a warning if interpenetration is too high."""
    if interpenetration > 1e-4:
        st.warning(
            f"The interpenetration area is {interpenetration:.2f} cm².\nPlease try again or increase the boundaries.",
            icon="⚠️",
        )


def plot_and_download(current_crowd: Crowd):
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
    backup_data_type = st.sidebar.selectbox(
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


def main():
    """Main function for the crowd tab."""
    st.info(
        "The computation of the random packing of the crowd is ongoing and may take some time. Please be patient.",
        icon="⏳",
    )

    initial_boundaries = create_boundaries(cst.DEFAULT_BOUNDARY_X, cst.DEFAULT_BOUNDARY_Y)
    current_crowd = update_crowd(initial_boundaries, cst.DEFAULT_AGENT_NUMBER)

    st.sidebar.header("General settings")
    # Rolling menu to select between ANSURII database / custom Database / Custom Statistics
    database_option = st.sidebar.selectbox(
        "Select database option:", options=["ANSURII database", "Custom database", "Custom statistics"]
    )
    boundary_x = st.sidebar.number_input(
        "Boundary X",
        min_value=cst.DEFAULT_BOUNDARY_X_MIN,
        max_value=cst.DEFAULT_BOUNDARY_X_MAX,
        value=cst.DEFAULT_BOUNDARY_X,
        step=1.0,
    )
    boundary_y = st.sidebar.number_input(
        "Boundary Y",
        min_value=cst.DEFAULT_BOUNDARY_Y_MIN,
        max_value=cst.DEFAULT_BOUNDARY_Y_MAX,
        value=cst.DEFAULT_BOUNDARY_Y,
        step=1.0,
    )
    new_boundaries = create_boundaries(boundary_x, boundary_y)
    # Display current options in the sidebar
    num_agents = st.sidebar.number_input(
        "Number of agents",
        min_value=cst.DEFAULT_AGENT_NUMBER_MIN,
        max_value=cst.DEFAULT_AGENT_NUMBER_MAX,
        value=current_crowd.get_number_agents(),
        step=1,
    )
    if database_option == "ANSURII database":
        current_crowd.measures.agent_statistics = {}
        current_crowd.measures.custom_database = {}
        current_crowd = update_crowd(new_boundaries, num_agents)
    elif database_option == "Custom database":
        st.sidebar.header(f"{database_option} settings")
        current_crowd.measures.agent_statistics = {}
        # Ask to upload a file with the desired dataset
        uploaded_file = st.sidebar.file_uploader("Upload custom dataset", type=["json", "xlsx"])
        if uploaded_file is not None:
            st.sidebar.success("File successfully uploaded!")
        # download the dataset example in data/json/ custom_crowd_example.json
        example_path = cst.JSON_DIR / "custom_crowd_example.json"
        with open(example_path, "r", encoding="utf8") as f:
            example_data = f.read()
        st.sidebar.download_button(
            label="Download example dataset", data=example_data, file_name="custom_crowd_example.json", mime="application/json"
        )
    else:  # Custom Statistics
        # set the default values for the statistics
        st.sidebar.header(f"{database_option} settings")
        male_proportion = cst.DEFAULT_MALE_PROPORTION
        male_chest_depth_mean = cst.DEFAULT_MALE_CHEST_DEPTH_MEAN
        male_bideltoid_breadth_mean = cst.DEFAULT_MALE_BIDELTOID_BREADTH_MEAN
        female_chest_depth_mean = cst.DEFAULT_FEMALE_CHEST_DEPTH_MEAN
        female_bideltoid_breadth_mean = cst.DEFAULT_FEMALE_BIDELTOID_BREADTH_MEAN
        wheel_width_mean = cst.DEFAULT_WHEEL_WIDTH_MEAN
        total_length_mean = cst.DEFAULT_TOTAL_LENGTH_MEAN
        handlebar_length_mean = cst.DEFAULT_HANDLEBAR_LENGTH_MEAN
        top_tube_length_mean = cst.DEFAULT_TOP_TUBE_LENGTH_MEAN

        pedestrian_proportion = st.sidebar.number_input(
            "Proportion of pedestrians",
            min_value=0.0,
            max_value=1.0,
            value=cst.DEFAULT_PEDESTRIAN_PROPORTION,
            step=0.1,
        )
        bike_proportion = st.sidebar.number_input(
            "Proportion of bikes",
            min_value=0.0,
            max_value=1.0,
            value=cst.DEFAULT_BIKE_PROPORTION,
            step=0.1,
        )
        if pedestrian_proportion > 0:
            male_proportion = st.sidebar.slider(
                "Proportion of male",
                min_value=0.0,
                max_value=1.0,
                value=cst.DEFAULT_MALE_PROPORTION,
                step=0.1,
            )
            if male_proportion != 0.0:
                male_chest_depth_mean = st.sidebar.slider(
                    "Male mean chest depth",
                    min_value=cst.DEFAULT_CHEST_DEPTH_MIN,
                    max_value=cst.DEFAULT_CHEST_DEPTH_MAX,
                    value=cst.DEFAULT_MALE_CHEST_DEPTH_MEAN,
                    step=1.0,
                )
                male_bideltoid_breadth_mean = st.sidebar.slider(
                    "Male mean bideltoid breadth",
                    min_value=cst.DEFAULT_BIDELTOID_BREADTH_MIN,
                    max_value=cst.DEFAULT_BIDELTOID_BREADTH_MAX,
                    value=cst.DEFAULT_MALE_BIDELTOID_BREADTH_MEAN,
                    step=1.0,
                )
            if male_proportion != 1.0:
                female_chest_depth_mean = st.sidebar.slider(
                    "Female mean chest depth",
                    min_value=cst.DEFAULT_CHEST_DEPTH_MIN,
                    max_value=cst.DEFAULT_CHEST_DEPTH_MAX,
                    value=cst.DEFAULT_FEMALE_CHEST_DEPTH_MEAN,
                    step=1.0,
                )
                female_bideltoid_breadth_mean = st.sidebar.slider(
                    "Female mean bideltoid breadth",
                    min_value=cst.DEFAULT_BIDELTOID_BREADTH_MIN,
                    max_value=cst.DEFAULT_BIDELTOID_BREADTH_MAX,
                    value=cst.DEFAULT_FEMALE_BIDELTOID_BREADTH_MEAN,
                    step=1.0,
                )
        if bike_proportion > 0.0:
            wheel_width_mean = st.sidebar.slider(
                "Wheel width mean",
                min_value=cst.DEFAULT_WHEEL_WIDTH_MIN,
                max_value=cst.DEFAULT_WHEEL_WIDTH_MAX,
                value=cst.DEFAULT_WHEEL_WIDTH_MEAN,
                step=1.0,
            )
            total_length_mean = st.sidebar.slider(
                "Total length mean",
                min_value=cst.DEFAULT_TOTAL_LENGTH_MIN,
                max_value=cst.DEFAULT_TOTAL_LENGTH_MAX,
                value=cst.DEFAULT_TOTAL_LENGTH_MEAN,
                step=1.0,
            )
            handlebar_length_mean = st.sidebar.slider(
                "Handlebar length mean",
                min_value=cst.DEFAULT_HANDLEBAR_LENGTH_MIN,
                max_value=cst.DEFAULT_HANDLEBAR_LENGTH_MAX,
                value=cst.DEFAULT_HANDLEBAR_LENGTH_MEAN,
                step=1.0,
            )
            top_tube_length_mean = st.sidebar.slider(
                "Top tube length mean",
                min_value=cst.DEFAULT_TOP_TUBE_LENGTH_MIN,
                max_value=cst.DEFAULT_TOP_TUBE_LENGTH_MAX,
                value=cst.DEFAULT_TOP_TUBE_LENGTH_MEAN,
                step=1.0,
            )

        current_crowd.measures.agent_statistics = {
            cst.CrowdStat.male_proportion.name: male_proportion,
            cst.CrowdStat.pedestrian_proportion.name: pedestrian_proportion,
            cst.CrowdStat.bike_proportion.name: bike_proportion,
            cst.CrowdStat.male_bideltoid_breadth_mean.name: male_bideltoid_breadth_mean,
            cst.CrowdStat.male_bideltoid_breadth_std_dev.name: cst.DEFAULT_MALE_BIDELTOID_BREADTH_STD_DEV,
            cst.CrowdStat.male_bideltoid_breadth_min.name: cst.DEFAULT_BIDELTOID_BREADTH_MIN,
            cst.CrowdStat.male_bideltoid_breadth_max.name: cst.DEFAULT_BIDELTOID_BREADTH_MAX,
            cst.CrowdStat.male_chest_depth_mean.name: male_chest_depth_mean,
            cst.CrowdStat.male_chest_depth_std_dev.name: cst.DEFAULT_MALE_CHEST_DEPTH_STD_DEV,
            cst.CrowdStat.male_chest_depth_min.name: cst.DEFAULT_CHEST_DEPTH_MIN,
            cst.CrowdStat.male_chest_depth_max.name: cst.DEFAULT_CHEST_DEPTH_MAX,
            cst.CrowdStat.female_bideltoid_breadth_mean.name: female_bideltoid_breadth_mean,
            cst.CrowdStat.female_bideltoid_breadth_std_dev.name: cst.DEFAULT_FEMALE_BIDELTOID_BREADTH_STD_DEV,
            cst.CrowdStat.female_bideltoid_breadth_min.name: cst.DEFAULT_BIDELTOID_BREADTH_MIN,
            cst.CrowdStat.female_bideltoid_breadth_max.name: cst.DEFAULT_BIDELTOID_BREADTH_MAX,
            cst.CrowdStat.female_chest_depth_mean.name: female_chest_depth_mean,
            cst.CrowdStat.female_chest_depth_std_dev.name: cst.DEFAULT_FEMALE_CHEST_DEPTH_STD_DEV,
            cst.CrowdStat.female_chest_depth_min.name: cst.DEFAULT_CHEST_DEPTH_MIN,
            cst.CrowdStat.female_chest_depth_max.name: cst.DEFAULT_CHEST_DEPTH_MAX,
            cst.CrowdStat.wheel_width_mean.name: wheel_width_mean,
            cst.CrowdStat.wheel_width_std_dev.name: cst.DEFAULT_WHEEL_WIDTH_STD_DEV,
            cst.CrowdStat.wheel_width_min.name: cst.DEFAULT_WHEEL_WIDTH_MIN,
            cst.CrowdStat.wheel_width_max.name: cst.DEFAULT_WHEEL_WIDTH_MAX,
            cst.CrowdStat.total_length_mean.name: total_length_mean,
            cst.CrowdStat.total_length_std_dev.name: cst.DEFAULT_TOTAL_LENGTH_STD_DEV,
            cst.CrowdStat.total_length_min.name: cst.DEFAULT_TOTAL_LENGTH_MIN,
            cst.CrowdStat.total_length_max.name: cst.DEFAULT_TOTAL_LENGTH_MAX,
            cst.CrowdStat.handlebar_length_mean.name: handlebar_length_mean,
            cst.CrowdStat.handlebar_length_std_dev.name: cst.DEFAULT_HANDLEBAR_LENGTH_STD_DEV,
            cst.CrowdStat.handlebar_length_min.name: cst.DEFAULT_HANDLEBAR_LENGTH_MIN,
            cst.CrowdStat.handlebar_length_max.name: cst.DEFAULT_HANDLEBAR_LENGTH_MAX,
            cst.CrowdStat.top_tube_length_mean.name: top_tube_length_mean,
            cst.CrowdStat.top_tube_length_std_dev.name: cst.DEFAULT_TOP_TUBE_LENGTH_STD_DEV,
            cst.CrowdStat.top_tube_length_min.name: cst.DEFAULT_TOP_TUBE_LENGTH_MIN,
            cst.CrowdStat.top_tube_length_max.name: cst.DEFAULT_TOP_TUBE_LENGTH_MAX,
        }
        current_crowd.create_agents(number_agents=num_agents)

    current_crowd.pack_agents_with_forces()
    interpenetration = current_crowd.calculate_interpenetration()
    display_interpenetration_warning(interpenetration)

    plot_and_download(current_crowd)


def run_tab_crowd():
    """Function to run the crowd tab."""
    main()
