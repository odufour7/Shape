"""2D Pedestrian Visualization Tab."""

from datetime import datetime
from pathlib import Path

import streamlit as st

import shapes.utils.constants as cst
from shapes.classes.agents import Agent
from shapes.classes.measures import AgentMeasures
from shapes.plotting import plot
from shapes.utils import functions as fun
from shapes.utils.typing_custom import BackupDataType


def main() -> None:
    """Run the main function for the 2D pedestrian tab."""
    st.sidebar.header("Select agent type")
    agent_type = st.sidebar.radio("Agent type", [cst.AgentTypes.pedestrian.name, cst.AgentTypes.bike.name])

    if str(agent_type) not in st.session_state:
        if agent_type == cst.AgentTypes.pedestrian.name:
            # Create a new pedestrian object
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian,
                measures={
                    "sex": cst.DEFAULT_SEX,
                    "bideltoid_breadth": cst.DEFAULT_BIDELTOID_BREADTH,
                    "chest_depth": cst.DEFAULT_CHEST_DEPTH,
                    "height": cst.DEFAULT_HEIGHT,
                    "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
                },
            )
            st.session_state.current_agent = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)
        elif agent_type == cst.AgentTypes.bike.name:
            # Create a new bike object
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.bike,
                measures={
                    "wheel_width": cst.DEFAULT_WHEEL_WIDTH,
                    "total_length": cst.DEFAULT_TOTAL_LENGTH,
                    "handlebar_length": cst.DEFAULT_HANDLEBAR_LENGTH,
                    "top_tube_length": cst.DEFAULT_TOP_TUBE_LENGTH,
                    "weight": cst.DEFAULT_BIKE_WEIGHT,
                },
            )
            st.session_state.current_agent = Agent(agent_type=cst.AgentTypes.bike, measures=agent_measures)
        else:  # default case
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian,
                measures={
                    "sex": cst.DEFAULT_SEX,
                    "bideltoid_breadth": cst.DEFAULT_BIDELTOID_BREADTH,
                    "chest_depth": cst.DEFAULT_CHEST_DEPTH,
                    "height": cst.DEFAULT_HEIGHT,
                    "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
                },
            )
            st.session_state.current_agent = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)
        st.session_state.agent_type = agent_type

    # Access the stored object
    current_agent = st.session_state.current_agent

    # Sidebar Sliders for Anthropometric Parameters
    st.sidebar.header("Adjust agent parameters")
    if agent_type == cst.AgentTypes.pedestrian.name:
        bideltoid_breadth = st.sidebar.slider(
            "Bideltoid breadth (cm)",
            min_value=cst.DEFAULT_BIDELTOID_BREADTH_MIN,
            max_value=cst.DEFAULT_BIDELTOID_BREADTH_MAX,
            value=cst.DEFAULT_BIDELTOID_BREADTH,
            step=1.0,
        )
        chest_depth = st.sidebar.slider(
            "Chest depth (cm)",
            min_value=cst.DEFAULT_CHEST_DEPTH_MIN,
            max_value=cst.DEFAULT_CHEST_DEPTH_MAX,
            value=cst.DEFAULT_CHEST_DEPTH,
            step=1.0,
        )
        agent_measures = AgentMeasures(
            agent_type=cst.AgentTypes.pedestrian,
            measures={
                "sex": cst.DEFAULT_SEX,
                "bideltoid_breadth": bideltoid_breadth,
                "chest_depth": chest_depth,
                "height": cst.DEFAULT_HEIGHT,
                "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
            },
        )
    elif agent_type == cst.AgentTypes.bike.name:
        wheel_width = st.sidebar.slider(
            "Wheel width (cm)",
            min_value=cst.DEFAULT_WHEEL_WIDTH_MIN,
            max_value=cst.DEFAULT_WHEEL_WIDTH_MAX,
            value=cst.DEFAULT_WHEEL_WIDTH,
            step=0.5,
        )
        total_length = st.sidebar.slider(
            "Total length (cm)",
            min_value=cst.DEFAULT_TOTAL_LENGTH_MIN,
            max_value=cst.DEFAULT_TOTAL_LENGTH_MAX,
            value=cst.DEFAULT_TOTAL_LENGTH,
            step=1.0,
        )
        handlebar_length = st.sidebar.slider(
            "Handlebar length (cm)",
            min_value=cst.DEFAULT_HANDLEBAR_LENGTH_MIN,
            max_value=cst.DEFAULT_HANDLEBAR_LENGTH_MAX,
            value=cst.DEFAULT_HANDLEBAR_LENGTH,
            step=1.0,
        )
        top_tube_length = st.sidebar.slider(
            "Top tube length (cm)",
            min_value=cst.DEFAULT_TOP_TUBE_LENGTH_MIN,
            max_value=cst.DEFAULT_TOP_TUBE_LENGTH_MAX,
            value=cst.DEFAULT_TOP_TUBE_LENGTH,
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

    st.sidebar.header("Adjust position")
    # Input fields for translation and rotation
    x_translation = st.sidebar.slider(
        "X-Translation (cm):", min_value=-cst.MAX_TRANSLATION_X, max_value=cst.MAX_TRANSLATION_X, value=0.0, step=1.0
    )
    y_translation = st.sidebar.slider(
        "Y-Translation (cm):", min_value=-cst.MAX_TRANSLATION_Y, max_value=cst.MAX_TRANSLATION_Y, value=0.0, step=1.0
    )
    rotation_angle = st.sidebar.slider(
        "Rotation angle (degrees):",
        min_value=-180.0,
        max_value=180.0,
        value=0.0,
        step=1.0,
    )

    current_agent.translate(x_translation, y_translation)
    current_agent.rotate(rotation_angle)

    # Main Page Content
    col1, col2 = st.columns([1.5, 1])  # Adjust proportions as needed
    with col1:
        st.subheader("Visualisation")
        fig = plot.display_shape2D([current_agent])
        st.plotly_chart(fig)
    with col2:
        # display the current agent measures
        st.subheader("Current agent measures:")
        if agent_type == cst.AgentTypes.pedestrian:
            path_file = Path(__file__).parent.parent.parent.parent / "data" / "images"
            st.image(path_file / "measures_pedestrian.png", use_container_width=True)
        elif agent_type == cst.AgentTypes.bike:
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

    # Create a select box for format selection
    backup_data_type: BackupDataType = st.sidebar.selectbox(
        "Select backup format:",
        options=["json", "xml"],
        format_func=lambda x: x.upper(),
        help="Choose the format for your data backup.",
    )

    # Add a download button
    filename = f"agent2D_{current_agent.agent_type}_{backup_data_type}_{timestamp}.{backup_data_type}"
    data, mime_type = fun.get_shapes_data(backup_data_type, current_agent.shapes2D.get_additional_parameters())
    st.sidebar.download_button(
        label=f"Download data as {backup_data_type.upper()}",
        data=data,
        file_name=filename,
        mime=mime_type,
    )


def run_tab_agent2D() -> None:
    """Execute the main function for the 2D pedestrian tab."""
    main()
