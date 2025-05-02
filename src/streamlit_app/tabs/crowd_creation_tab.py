"""Pedestrian visualization tab."""

import pickle
from datetime import datetime
from io import BytesIO

import numpy as np
import streamlit as st
from shapely.geometry import Polygon

import configuration.backup.crowd_to_dict as fun_dict
import configuration.backup.crowd_to_zip_and_reverse as fun_zip
import configuration.backup.dict_to_xml_and_reverse as fun_xml
import configuration.utils.constants as cst
import configuration.utils.functions as fun
import streamlit_app.utils.constants as cst_app
from configuration.models.crowd import Crowd, create_agents_from_dynamic_static_geometry_parameters
from configuration.models.measures import CrowdMeasures
from configuration.utils.typing_custom import DynamicCrowdDataType, GeometryDataType, StaticCrowdDataType
from streamlit_app.plot import plot


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    default_values = {
        "pedestrian_proportion": cst.CrowdStat["pedestrian_proportion"],
        "bike_proportion": cst.CrowdStat["bike_proportion"],
        "male_proportion": cst.CrowdStat["male_proportion"],
        "male_chest_depth_mean": cst.CrowdStat["male_chest_depth_mean"],
        "male_bideltoid_breadth_mean": cst.CrowdStat["male_bideltoid_breadth_mean"],
        "female_chest_depth_mean": cst.CrowdStat["female_chest_depth_mean"],
        "female_bideltoid_breadth_mean": cst.CrowdStat["female_bideltoid_breadth_mean"],
        "wheel_width_mean": cst.CrowdStat["wheel_width_mean"],
        "total_length_mean": cst.CrowdStat["total_length_mean"],
        "handlebar_length_mean": cst.CrowdStat["handlebar_length_mean"],
        "top_tube_length_mean": cst.CrowdStat["top_tube_length_mean"],
        "boundary_x": cst_app.DEFAULT_BOUNDARY_X,
        "boundary_y": cst_app.DEFAULT_BOUNDARY_Y,
        "pedestrian_weight": cst.CrowdStat["pedestrian_weight_mean"],
        "bike_weight": cst.CrowdStat["bike_weight_mean"],
        "repulsion_length": cst_app.DEFAULT_REPULSION_LENGTH_MIN,
        "wall_interaction": cst_app.DEFAULT_WALL_INTERACTION,
        "simulation_run": True,
        "desired_direction": cst.DEFAULT_DESIRED_DIRECTION,
        "variable_orientation": False,
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
    interpenetration_between_agents, interpenetration_with_boundaries = st.session_state.current_crowd.calculate_interpenetration()
    if interpenetration_between_agents > 1e-4:
        st.warning(
            f"The interpenetration area **between agents** is {interpenetration_between_agents:.2f} cm².\n"
            + "Please rerun or increase the boundaries.",
            icon="⚠️",
        )
    if st.session_state.wall_interaction:
        if interpenetration_with_boundaries > 1e-4:
            st.warning(
                f"The interpenetration area **with boundaries** is {interpenetration_with_boundaries:.2f} cm².\n"
                + "Please rerun or increase the boundaries.",
                icon="⚠️",
            )


def display_crowd_statistics(crowd_statistics_measures: dict[str, float | int | None]) -> None:
    """
    Display crowd statistics in a Streamlit app.

    Parameters
    ----------
    crowd_statistics_measures : dict[str, float | int | None]
        A dictionary containing crowd statistics measures.
    """
    filtered_measures = fun.filter_dict_by_not_None_values(crowd_statistics_measures)

    st.write("### Measured crowd statistics")

    # Display as a Markdown table for better readability
    if filtered_measures:
        table_md = "| Measure | Value |\n|---|---|\n"
        for key, value in filtered_measures.items():
            table_md += f"| {key.capitalize()} | {np.round(value, 2)} |\n"
        st.markdown(table_md)
    else:
        st.info("No statistics available to display.")


def plot_and_download_crowd2D(current_crowd: Crowd) -> None:
    """
    Plot the crowd and provide download options.

    Parameters
    ----------
    current_crowd : Crowd
        The Crowd object to be plotted and downloaded.
    """
    crowd_statistics = current_crowd.get_crowd_statistics()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Download section
    st.sidebar.header("Download")
    # check if all agents in the Crowd are pedestrian
    if all(agent.agent_type == cst.AgentTypes.pedestrian for agent in current_crowd.agents):
        filename = f"crowd2D_{timestamp}.zip"
        zip_buffer = fun_zip.write_crowd_data_to_zip(current_crowd)

        # Add download button for the ZIP file
        st.sidebar.download_button(
            label="Export crowd as XML configuration files",
            data=zip_buffer,
            file_name=filename,
            mime="application/zip",
        )

        if cst_app.SHOW_DEV:
            filename = f"crowd2D_{timestamp}.xml"
            data_dict = fun_dict.get_light_agents_params(current_crowd)
            data = fun_xml.save_light_agents_params_dict_to_xml(data_dict)
            st.sidebar.download_button(
                label="Download basic information about the crowd as a single XML file",
                data=data,
                file_name=filename,
                mime="application/xml",
            )

        # Download the crowd statistics as a CSV file
        filename = f"crowd_statistics_{timestamp}.csv"
        data = fun.get_csv_buffer(crowd_statistics["stats_lists"])
        st.sidebar.download_button(
            label="Export distributions as CSV",
            data=data,
            file_name=filename,
            mime="text/csv",
        )

    else:
        filename = f"crowd2D_{timestamp}.xml"
        data_dict = fun_dict.get_light_agents_params(current_crowd)
        data = fun_xml.save_light_agents_params_dict_to_xml(data_dict)
        st.sidebar.download_button(
            label="Download basic information about the crowd as a single XML file",
            data=data,
            file_name=filename,
            mime="application/xml",
        )

        # Download the crowd statistics as a CSV file
        filename = f"crowd_statistics_{timestamp}.csv"
        data = fun.get_csv_buffer(crowd_statistics["stats_lists"])
        st.download_button(
            label="Export crowd observation distributions as a CSV.",
            data=data,
            file_name=filename,
            mime="text/csv",
        )

    # Display section
    col1, _ = st.columns([1.5, 1])
    with col1:
        st.subheader("Visualisation")
        fig = plot.display_crowd2D(current_crowd)
        st.pyplot(fig)

        crowd_plot = BytesIO()
        fig.savefig(crowd_plot, format="pdf")
        crowd_plot.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Download plot as PDF",
            data=crowd_plot,
            file_name=f"crowd_{timestamp}.pdf",
            mime="application/pdf",
        )
    display_crowd_statistics(crowd_statistics["measures"])


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
                min_value=cst.CrowdStat["male_chest_depth_min"],
                max_value=cst.CrowdStat["male_chest_depth_max"],
                value=st.session_state.male_chest_depth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.male_chest_depth_mean = male_chest_depth_mean
            male_bideltoid_breadth_mean = st.sidebar.slider(
                "Male mean bideltoid breadth",
                min_value=cst.CrowdStat["male_bideltoid_breadth_min"],
                max_value=cst.CrowdStat["male_bideltoid_breadth_max"],
                value=st.session_state.male_bideltoid_breadth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.male_bideltoid_breadth_mean = male_bideltoid_breadth_mean
        if st.session_state.male_proportion != 1.0:
            female_chest_depth_mean = st.sidebar.slider(
                "Female mean chest depth",
                min_value=cst.CrowdStat["male_chest_depth_min"],
                max_value=cst.CrowdStat["male_chest_depth_max"],
                value=st.session_state.male_chest_depth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.female_chest_depth_mean = female_chest_depth_mean
            female_bideltoid_breadth_mean = st.sidebar.slider(
                "Female mean bideltoid breadth",
                min_value=cst.CrowdStat["male_bideltoid_breadth_min"],
                max_value=cst.CrowdStat["male_bideltoid_breadth_max"],
                value=st.session_state.female_bideltoid_breadth_mean,
                step=1.0,
                on_change=parameter_changed,
            )
            st.session_state.female_bideltoid_breadth_mean = female_bideltoid_breadth_mean
    if st.session_state.bike_proportion > 0.0:
        wheel_width_mean = st.sidebar.slider(
            "Wheel width mean",
            min_value=cst.CrowdStat["wheel_width_min"],
            max_value=cst.CrowdStat["wheel_width_max"],
            value=st.session_state.wheel_width_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.wheel_width_mean = wheel_width_mean
        total_length_mean = st.sidebar.slider(
            "Total length mean",
            min_value=cst.CrowdStat["total_length_min"],
            max_value=cst.CrowdStat["total_length_max"],
            value=st.session_state.total_length_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.total_length_mean = total_length_mean
        handlebar_length_mean = st.sidebar.slider(
            "Handlebar length mean",
            min_value=cst.CrowdStat["handlebar_length_min"],
            max_value=cst.CrowdStat["handlebar_length_max"],
            value=st.session_state.handlebar_length_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.handlebar_length_mean = handlebar_length_mean
        top_tube_length_mean = st.sidebar.slider(
            "Top tube length mean",
            min_value=cst.CrowdStat["top_tube_length_min"],
            max_value=cst.CrowdStat["top_tube_length_max"],
            value=st.session_state.top_tube_length_mean,
            step=1.0,
            on_change=parameter_changed,
        )
        st.session_state.top_tube_length_mean = top_tube_length_mean
    # Initialize agent_statistics with default values from cst.CrowdStat
    agent_statistics = cst.CrowdStat.copy()

    # Override specific values with st.session_state where applicable
    agent_statistics.update(
        {
            "male_proportion": st.session_state.male_proportion,
            "pedestrian_proportion": st.session_state.pedestrian_proportion,
            "bike_proportion": st.session_state.bike_proportion,
            "male_bideltoid_breadth_mean": st.session_state.male_bideltoid_breadth_mean,
            "male_chest_depth_mean": st.session_state.male_chest_depth_mean,
            "female_bideltoid_breadth_mean": st.session_state.female_bideltoid_breadth_mean,
            "female_chest_depth_mean": st.session_state.female_chest_depth_mean,
            "wheel_width_mean": st.session_state.wheel_width_mean,
            "total_length_mean": st.session_state.total_length_mean,
            "handlebar_length_mean": st.session_state.handlebar_length_mean,
        }
    )
    crowd_measures = CrowdMeasures(agent_statistics=agent_statistics)
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

    variable_orientation: bool = st.sidebar.checkbox("Variable orientation", value=False, on_change=parameter_changed)
    if variable_orientation != st.session_state.variable_orientation:
        st.session_state.variable_orientation = variable_orientation

    wall_interaction: bool = st.sidebar.checkbox(
        "Enable wall interaction",
        on_change=parameter_changed,
    )
    if wall_interaction != st.session_state.wall_interaction:
        st.session_state.wall_interaction = wall_interaction

    new_boundaries = boundaries_state()

    repulsion_length: float = st.sidebar.slider(
        "Initial spacing (cm)",
        min_value=cst_app.DEFAULT_REPULSION_LENGTH_MIN,
        max_value=cst_app.DEFAULT_REPULSION_LENGTH_MAX,
        value=cst.DEFAULT_REPULSION_LENGTH,
        step=0.01,
        on_change=parameter_changed,
    )
    if repulsion_length != st.session_state.repulsion_length:
        st.session_state.repulsion_length = repulsion_length

    return new_boundaries


def run_crowd_init() -> None:
    """
    Provide an interactive interface for simulating and visualizing a crowd of agents.

    Users can configure general settings, select databases, and control agent packing behavior.
    The tab includes options for crowd visualization and downloading results.

    Attributes
    ----------
    Main Page:
        - Crowd visualization using Plotly charts.
        - Interpenetration warnings if applicable.

    Notes
    -----
    - Sidebar:
        - General settings:
            - Toggle for packing agents.
            - Input fields for boundaries, number of agents, wall interaction strength, and repulsion length.
        - Database selection:
            - Options: ANSURII database, Custom statistics.
            - Additional settings for custom statistics.
        - Download options:
            - Export results as files.
    - If agent packing is enabled, agents are packed using force-based interactions.
      Otherwise, the crowd is unpacked.
    - Interpenetration between agents is calculated and displayed as a warning if necessary.
    """
    # Initialize session state variables
    initialize_session_state()

    st.sidebar.header("General settings")

    new_boundaries = general_settings()

    # Rolling menu to select between ANSURII database  / Custom Statistics
    database_option = st.sidebar.selectbox(
        "Select database origin",
        options=["ANSURII database", "Custom statistics"],
    )
    if "database_option" not in st.session_state:
        st.session_state.database_option = database_option

    if database_option == "ANSURII database":
        if st.session_state.simulation_run:
            info_placeholder = st.empty()
            info_placeholder.info(
                "The agents creation is ongoing and may take some time. Please be patient.",
                icon="⏳",
            )
            current_crowd = Crowd(boundaries=new_boundaries)
            current_crowd.create_agents(st.session_state.num_agents)
            st.session_state.current_crowd = current_crowd
            info_placeholder.empty()

    else:  # Custom Statistics
        st.sidebar.header(f"{database_option} settings")
        agent_statistics_state(new_boundaries, st.session_state.num_agents)

    if st.session_state.simulation_run:
        info_placeholder = st.empty()
        info_placeholder.info(
            "The packing of the crowd is ongoing and may take some time. Please be patient.",
            icon="⏳",
        )
        st.session_state.current_crowd.pack_agents_with_forces(
            st.session_state.repulsion_length, st.session_state.desired_direction, st.session_state.variable_orientation
        )
        st.session_state.simulation_run = False
        info_placeholder.empty()

    display_interpenetration_warning()

    # Choose between 2D representation of the crowd or 3D representation
    st.subheader("Choose dimension")
    plot_2D_3D_and_download_section(st.session_state.current_crowd)


def plot_2D_3D_and_download_section(current_crowd: Crowd) -> None:
    """
    Display options to plot the current crowd in 2D or 3D and provide download functionality.

    Depending on the agent types in the crowd, this function presents the user with options
    to visualize the crowd either in 2D or 3D. If all agents are of type `pedestrian`, both
    2D and 3D visualization options are available. Otherwise, only 2D visualization is offered.
    The function also enables downloading the plotted results.

    Parameters
    ----------
    current_crowd : Crowd
        The crowd object containing agent data to be visualized.
    """
    if all(agent.agent_type == cst.AgentTypes.pedestrian for agent in current_crowd.agents):
        dimension_options = {
            "2D crowd": "2D",
            "3D crowd": "3D",
        }
        selected_dimension_options = st.pills(" ", list(dimension_options.values()), label_visibility="collapsed", default="2D")
        # Plotting and downloading
        if selected_dimension_options == dimension_options["2D crowd"]:
            plot_and_download_crowd2D(current_crowd)
        elif selected_dimension_options == dimension_options["3D crowd"]:
            plot_and_download_crowd3D(current_crowd)
    else:
        dimension_options = {"2D crowd": "2D"}
        selected_dimension_options = st.pills(" ", list(dimension_options.values()), label_visibility="collapsed", default="2D")
        # Plotting and downloading
        if selected_dimension_options == dimension_options["2D crowd"]:
            plot_and_download_crowd2D(current_crowd)


def run_crowd_from_config() -> None:
    """
    Run the crowd simulation from uploaded XML configuration files.

    This function provides a Streamlit sidebar interface for uploading three required XML files:
    Agents.xml, Geometry.xml, and AgentDynamics.xml. It validates the uploads, parses the XML files
    into dictionaries, creates a crowd object using the configuration, displays a 2D plot of the crowd,
    and allows the user to download the plot as a PDF.

    Notes
    -----
    - All three configuration files must be uploaded to proceed.
    - Displays errors or info messages in the Streamlit sidebar if files are missing or invalid.
    """
    # --- File upload section ---
    st.sidebar.header("Upload configuration files")
    uploaded_dynamics = st.sidebar.file_uploader("Upload AgentDynamics.xml", type="xml", key="AgentDynamics")
    uploaded_agents = st.sidebar.file_uploader("Upload Agents.xml", type="xml", key="Agents")
    uploaded_geometry = st.sidebar.file_uploader("Upload Geometry.xml", type="xml", key="Geometry")

    # --- File validation ---
    files = {
        "Agents.xml": uploaded_agents,
        "Geometry.xml": uploaded_geometry,
        "AgentDynamics.xml": uploaded_dynamics,
    }
    missing_files = [name for name, file in files.items() if file is None or (hasattr(file, "size") and file.size == 0)]
    if missing_files:
        for name in missing_files:
            st.error(f"{name} is missing or empty. Please upload a valid file.")
        st.info("Please upload all three configuration files to continue.")

    # --- XML Parsing ---
    if all(file is not None and (not hasattr(file, "size") or file.size > 0) for file in files.values()):
        crowd_xml: str = uploaded_agents.read().decode("utf-8")  # type: ignore
        static_dict: StaticCrowdDataType = fun_xml.static_xml_to_dict(crowd_xml)

        geometry_xml: str = uploaded_geometry.read().decode("utf-8")  # type: ignore
        geometry_dict: GeometryDataType = fun_xml.geometry_xml_to_dict(geometry_xml)

        dynamic_xml: str = uploaded_dynamics.read().decode("utf-8")  # type: ignore
        dynamic_dict: DynamicCrowdDataType = fun_xml.dynamic_xml_to_dict(dynamic_xml)

        # --- Crowd creation ---
        try:
            current_crowd = create_agents_from_dynamic_static_geometry_parameters(
                static_dict=static_dict,
                dynamic_dict=dynamic_dict,
                geometry_dict=geometry_dict,
            )

            # --- Plotting and downloading ---
            st.subheader("Choose dimension")
            plot_2D_3D_and_download_section(current_crowd)
        except ValueError as e:
            st.error(f"Value error while creating crowd: {e}")
        except KeyError as e:
            st.error(f"Key error while creating crowd: {e}")
        except TypeError as e:
            st.error(f"Type error while creating crowd: {e}")


def plot_and_download_crowd_from_config(current_crowd: Crowd) -> None:
    """
    Plot and download the plot of the crowd from configuration files.

    Parameters
    ----------
    current_crowd : Crowd
        The Crowd object to be plotted and downloaded.
    """
    # --- Plotting ---
    col1, _ = st.columns([1.5, 1])
    with col1:
        fig = plot.display_crowd2D(current_crowd)
        st.pyplot(fig)

        # --- Download section ---
        crowd_plot = BytesIO()
        fig.savefig(crowd_plot, format="pdf")
        crowd_plot.seek(0)

        st.sidebar.header("Download")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Download plot as PDF",
            data=crowd_plot,
            file_name=f"crowd_{timestamp}.pdf",
            mime="application/pdf",
        )


def plot_and_download_crowd3D(current_crowd: Crowd) -> None:
    """
    Plot the crowd in 3D and provide download options.

    Parameters
    ----------
    current_crowd : Crowd
        The Crowd object to be plotted and downloaded.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    st.sidebar.header("Download")

    filename = f"crowd3D_{timestamp}.pkl"
    data_to_download = pickle.dumps([current_pedestrian.shapes3D.shapes for current_pedestrian in current_crowd.agents])
    st.sidebar.download_button(
        label="Export 3D crowd data as PKL",
        data=data_to_download,
        file_name=filename,
        mime="application/octet-stream",
        help="This will download the 3D crowd data as "
        "a list of dict[float, MultiPolygon], "
        "i.e. one dictionary for each agent, "
        "as a pickle file.",
    )

    st.subheader("Visualisation")
    col1, col2 = st.columns([1, 1])

    with col1:
        fig = plot.display_crowd3D_whole_3Dscene(current_crowd)
        st.plotly_chart(fig)

    with col2:
        st.text(" ")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        st.text(" ")
        fig = plot.display_crowd3D_layers_by_layers(current_crowd)
        st.plotly_chart(fig)


def run_tab_crowd() -> None:
    """
    Display and manage the crowd setup tab in the Streamlit app.

    This function allows the user to either initialize a new crowd and save configuration files,
    or to create a crowd using existing configuration files by uploading them. The function
    handles file validation, parsing, crowd creation, visualization, and plot download.
    """
    st.subheader("Select the crowd setup method")
    crowd_origin_options = {
        "init crowd": "Initialize your own crowd",
        "crowd from config": "Generate from configuration files",
    }
    selected_crowd_origin = st.pills(" ", list(crowd_origin_options.values()), label_visibility="collapsed")

    if selected_crowd_origin == crowd_origin_options["init crowd"]:
        run_crowd_init()

    if selected_crowd_origin == crowd_origin_options["crowd from config"]:
        run_crowd_from_config()
