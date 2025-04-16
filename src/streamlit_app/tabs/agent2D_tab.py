"""2D pedestrian visualization tab."""

from datetime import datetime
from pathlib import Path

import streamlit as st

import configuration.utils.constants as cst
import streamlit_app.utils.constants as cst_app
from configuration.models.agents import Agent
from configuration.models.measures import AgentMeasures
from streamlit_app.plot import plot


def init_session_state() -> AgentMeasures:
    """
    Initialize session state variables for different agent types (pedestrian or bike).

    Attributes
    ----------
    - `st.session_state.agent_type_measures`: Stores the selected agent type.
    - `st.session_state.current_agent`: Stores the initialized `Agent` object for the selected agent type.
    - `st.session_state.agent_type`: Stores the name of the selected agent type.

    Returns
    -------
    AgentMeasures
        An object containing the initialized measures for the selected agent type.

    Notes
    -----
    - For pedestrians, default measures include attributes like sex, bideltoid breadth,
      chest depth, height, and weight.
    - For bikes, default measures include attributes like wheel width, total length,
      handlebar length, top tube length, and weight.
    - The function uses Streamlit's `st.sidebar.radio` to allow users to select the agent type.
    """
    agent_type: str = st.sidebar.radio("Agent type", [cst.AgentTypes.pedestrian.name, cst.AgentTypes.bike.name])

    if str(agent_type) not in st.session_state:
        if agent_type == cst.AgentTypes.pedestrian.name:
            # Create a new pedestrian object
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian,
                measures={
                    "sex": cst_app.DEFAULT_SEX,
                    "bideltoid_breadth": cst.CrowdStat["male_bideltoid_breadth_mean"],
                    "chest_depth": cst.CrowdStat["male_chest_depth_mean"],
                    "height": cst_app.DEFAULT_PEDESTRIAN_HEIGHT,
                    "weight": cst.CrowdStat["pedestrian_weight_mean"],
                },
            )
            st.session_state.agent_type_measures = cst.AgentTypes.pedestrian
            st.session_state.current_agent = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)
            st.session_state.current_agent.rotate(-90.0)  # rotate the pedestrian to face the positive x-axis
        elif agent_type == cst.AgentTypes.bike.name:
            # Create a new bike object
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.bike,
                measures={
                    "wheel_width": cst.CrowdStat["wheel_width_mean"],
                    "total_length": cst.CrowdStat["total_length_mean"],
                    "handlebar_length": cst.CrowdStat["handlebar_length_mean"],
                    "top_tube_length": cst.CrowdStat["top_tube_length_mean"],
                    "weight": cst.CrowdStat["bike_weight_mean"],
                },
            )
            st.session_state.agent_type_measures = cst.AgentTypes.bike
            st.session_state.current_agent = Agent(agent_type=cst.AgentTypes.bike, measures=agent_measures)
        else:  # default case
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian,
                measures={
                    "sex": cst_app.DEFAULT_SEX,
                    "bideltoid_breadth": cst.CrowdStat["male_bideltoid_breadth_mean"],
                    "chest_depth": cst.CrowdStat["male_chest_depth_mean"],
                    "height": cst_app.DEFAULT_PEDESTRIAN_HEIGHT,
                    "weight": cst.CrowdStat["pedestrian_weight_mean"],
                },
            )
            st.session_state.agent_type_measures = cst.AgentTypes.pedestrian
            st.session_state.current_agent = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)
        st.session_state.agent_type = agent_type

    return agent_measures


def sliders_for_agent_measures(agent_measures: AgentMeasures) -> None:
    """
    Create sliders in the sidebar to adjust agent measures.

    Parameters
    ----------
    agent_measures : AgentMeasures
        The current `AgentMeasures` object that holds the measures for the selected agent type.

    Attributes
    ----------
    - `st.session_state.current_agent`: The updated `Agent` object with modified measures.

    Notes
    -----
    - For pedestrians:
        - Sliders are created for `bideltoid_breadth` and `chest_depth`.
        - Other measures (e.g., height, weight, and sex) are set to default values.
    - For bikes:
        - Sliders are created for `wheel_width`, `total_length`, `handlebar_length`, and `top_tube_length`.
        - Other measures (e.g., weight) are set to default values.
    """
    current_agent = st.session_state.current_agent
    if st.session_state.agent_type == cst.AgentTypes.pedestrian.name:
        bideltoid_breadth = st.sidebar.slider(
            "Bideltoid breadth (cm)",
            min_value=cst.CrowdStat["male_bideltoid_breadth_min"],
            max_value=cst.CrowdStat["male_bideltoid_breadth_max"],
            value=cst.CrowdStat["male_bideltoid_breadth_mean"],
            step=1.0,
        )
        chest_depth = st.sidebar.slider(
            "Chest depth (cm)",
            min_value=cst.CrowdStat["male_chest_depth_min"],
            max_value=cst.CrowdStat["male_chest_depth_max"],
            value=cst.CrowdStat["male_chest_depth_mean"],
            step=1.0,
        )
        agent_measures = AgentMeasures(
            agent_type=cst.AgentTypes.pedestrian,
            measures={
                "sex": cst_app.DEFAULT_SEX,
                "bideltoid_breadth": bideltoid_breadth,
                "chest_depth": chest_depth,
                "height": cst_app.DEFAULT_PEDESTRIAN_HEIGHT,
                "weight": cst.CrowdStat["pedestrian_weight_mean"],
            },
        )
    elif st.session_state.agent_type == cst.AgentTypes.bike.name:
        wheel_width = st.sidebar.slider(
            "Wheel width (cm)",
            min_value=cst.CrowdStat["wheel_width_min"],
            max_value=cst.CrowdStat["wheel_width_max"],
            value=cst.CrowdStat["wheel_width_mean"],
            step=0.5,
        )
        total_length = st.sidebar.slider(
            "Total length (cm)",
            min_value=cst.CrowdStat["total_length_min"],
            max_value=cst.CrowdStat["total_length_max"],
            value=cst.CrowdStat["total_length_mean"],
            step=1.0,
        )
        handlebar_length = st.sidebar.slider(
            "Handlebar length (cm)",
            min_value=cst.CrowdStat["handlebar_length_min"],
            max_value=cst.CrowdStat["handlebar_length_max"],
            value=cst.CrowdStat["handlebar_length_mean"],
            step=1.0,
        )
        top_tube_length = st.sidebar.slider(
            "Top tube length (cm)",
            min_value=cst.CrowdStat["top_tube_length_min"],
            max_value=cst.CrowdStat["top_tube_length_max"],
            value=cst.CrowdStat["top_tube_length_mean"],
            step=1.0,
        )
        agent_measures = AgentMeasures(
            agent_type=cst.AgentTypes.bike,
            measures={
                "wheel_width": wheel_width,
                "total_length": total_length,
                "handlebar_length": handlebar_length,
                "top_tube_length": top_tube_length,
                "weight": cst.DEFAULT_BIKE_WEIGHT,
            },
        )

    current_agent.measures = agent_measures


def sliders_for_position() -> tuple[float, float, float]:
    """
    Create sliders in the sidebar for position and rotation adjustments.

    Returns
    -------
    tuple[float, float, float]
        A tuple containing:
        - `x_translation` (float): The translation along the X-axis in centimeters.
        - `y_translation` (float): The translation along the Y-axis in centimeters.
        - `rotation_angle` (float): The rotation angle in degrees.
    """
    x_translation = st.sidebar.slider(
        "X-translation (cm):", min_value=-cst_app.MAX_TRANSLATION_X, max_value=cst_app.MAX_TRANSLATION_X, value=0.0, step=1.0
    )
    y_translation = st.sidebar.slider(
        "Y-translation (cm):", min_value=-cst_app.MAX_TRANSLATION_Y, max_value=cst_app.MAX_TRANSLATION_Y, value=0.0, step=1.0
    )
    rotation_angle = st.sidebar.slider(
        "Rotation angle (degrees):",
        min_value=-180.0,
        max_value=180.0,
        value=0.0,
        step=1.0,
    )
    return x_translation, y_translation, rotation_angle


def run_tab_agent2D() -> None:
    """
    Provide an interactive interface for visualizing 2D representations of agents (e.g. pedestrians or bikes).

    Attributes
    ----------
    Sidebar:
        - Agent type selection.
        - Sliders for anthropometric parameters (e.g., measures).
        - Sliders for position and rotation.
    Main Page:
        - Visualization of the 2D agent shape.
        - Display of current agent measures with corresponding images.
    """
    st.sidebar.header("Select agent type")

    # Initialize session state variables
    agent_measures = init_session_state()

    # Access the stored object
    current_agent = st.session_state.current_agent

    # Input fields for Anthropometric parameters
    st.sidebar.header("Adjust agent parameters")
    sliders_for_agent_measures(agent_measures)

    # Input fields for translation and rotation
    st.sidebar.header("Adjust position")
    x_translation, y_translation, rotation_angle = sliders_for_position()
    current_agent.translate(x_translation, y_translation)
    current_agent.rotate(rotation_angle)

    # Main page content
    col1, col2 = st.columns([1.5, 1])  # Adjust proportions as needed
    with col1:
        st.subheader("Visualisation")
        fig = plot.display_shape2D([current_agent])
        st.plotly_chart(fig)
    with col2:
        # display the current agent measures
        st.subheader("Current agent measures:")
        if st.session_state.agent_type_measures == cst.AgentTypes.pedestrian:
            path_file = Path(__file__).parent.parent.parent.parent / "data" / "images"
            st.image(path_file / "measures_pedestrian.png", use_container_width=True)
        elif st.session_state.agent_type_measures == cst.AgentTypes.bike:
            path_file = Path(__file__).parent.parent.parent.parent / "data" / "images"
            st.image(path_file / "measures_bike.png", use_container_width=True)

    st.sidebar.header("Download")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.sidebar.download_button(
        label="Download plot as PDF",
        data=fig.to_image(format="pdf"),
        file_name=f"body2D_orthogonal_projection_{timestamp}.pdf",
        mime="application/pdf",
    )
