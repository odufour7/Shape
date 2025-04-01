"""Custom Crowd Tab."""

from datetime import datetime

import streamlit as st

import shapes.utils.constants as cst
from shapes.classes.agents import Agent
from shapes.classes.measures import AgentMeasures
from shapes.plotting import plot
from shapes.utils import functions as fun
from shapes.utils.typing_custom import BackupDataType, Sex, ShapeDataType


# Helper function to initialize session state
def initialize_session_state() -> None:
    """Initialize the session state variables."""
    if "agents" not in st.session_state:
        st.session_state.agents = []
    if "current_agent_id" not in st.session_state:
        st.session_state.current_agent_id = None
    if "simulation_run" not in st.session_state:
        st.session_state.simulation_run = True


def parameter_changed() -> None:
    """Update the Streamlit session state to indicate that a simulation should be run."""
    st.session_state.simulation_run = True


# Helper function to add a new agent
def add_agent(agent_type: cst.AgentTypes) -> None:
    """
    Add a new agent of the specified type to the session state.

    Parameters
    ----------
    agent_type : AgentType
        The type of agent to be added (e.g., pedestrian or bike).
    """
    default_measures: dict[cst.AgentTypes, dict[str, float | Sex]] = {
        cst.AgentTypes.pedestrian: {
            "sex": cst.DEFAULT_SEX,
            "bideltoid_breadth": cst.DEFAULT_BIDELTOID_BREADTH,
            "chest_depth": cst.DEFAULT_CHEST_DEPTH,
            "height": cst.DEFAULT_HEIGHT,
            "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
        },
        cst.AgentTypes.bike: {
            "wheel_width": cst.DEFAULT_WHEEL_WIDTH,
            "total_length": cst.DEFAULT_TOTAL_LENGTH,
            "handlebar_length": cst.DEFAULT_HANDLEBAR_LENGTH,
            "top_tube_length": cst.DEFAULT_TOP_TUBE_LENGTH,
            "weight": cst.DEFAULT_BIKE_WEIGHT,
        },
    }

    agent_measures = AgentMeasures(
        agent_type=agent_type,
        measures=default_measures[agent_type],
    )
    new_agent = Agent(agent_type=agent_type, measures=agent_measures)
    st.session_state.agents.append(new_agent)
    st.session_state.current_agent_id = len(st.session_state.agents) - 1


# Helper function to remove an agent safely
def remove_agent(selected_id: int) -> None:
    """
    Remove an agent from the session state by its ID.

    Parameters
    ----------
    selected_id : int
        The ID of the agent to be removed. You can use the number displayed directly on the Streamlit app.

    Notes
    -----
    - Modifies the 'agents' list in the session state by removing the agent with the given ID.
    - Updates 'current_agent_id' in the session state to the next valid agent ID or None if no agents remain.
    - Calls 'st.rerun()' if no agents remain to refresh the Streamlit app.
    """
    agents = st.session_state.agents
    if 0 <= selected_id < len(agents):
        del agents[selected_id]
        if agents:
            st.session_state.current_agent_id = min(selected_id, len(agents) - 1)
        else:
            st.session_state.current_agent_id = None
            st.rerun()


def sliders_for_agent_parameters(selected_id: int, current_agent: Agent) -> None:
    """
    Create sliders in the sidebar to adjust parameters for a specific agent.

    Parameters
    ----------
    selected_id : int
        A unique identifier for the selected agent. Used as a key for Streamlit widgets
        to ensure uniqueness.
    current_agent : Agent
        The agent object whose parameters are being modified. This object contains
        measures and other attributes specific to the agent type.

    Notes
    -----
    - For pedestrians, sliders are created for `bideltoid_breadth`, `chest_depth`, and `weight`.
    - For bikes, sliders are created for `wheel_width`, `total_length`, `handlebar_length`, `top_tube_length`, and `weight`.
    - The `on_change` callback (`parameter_changed`) is triggered whenever a slider value is modified.
    """
    if current_agent.agent_type.name == cst.AgentTypes.pedestrian.name:
        current_agent.measures.measures["bideltoid_breadth"] = st.sidebar.slider(
            "Bideltoid breadth (cm)",
            cst.DEFAULT_BIDELTOID_BREADTH_MIN,
            cst.DEFAULT_BIDELTOID_BREADTH_MAX,
            value=current_agent.measures.measures["bideltoid_breadth"],
            step=1.0,
            key=f"bideltoid_{selected_id}",
            on_change=parameter_changed,
        )
        current_agent.measures.measures["chest_depth"] = st.sidebar.slider(
            "Chest depth (cm)",
            cst.DEFAULT_CHEST_DEPTH_MIN,
            cst.DEFAULT_CHEST_DEPTH_MAX,
            value=current_agent.measures.measures["chest_depth"],
            step=1.0,
            key=f"chest_{selected_id}",
            on_change=parameter_changed,
        )
        current_agent.measures.measures["weight"] = st.sidebar.slider(
            "Weight (kg)",
            cst.DEFAULT_PEDESTRIAN_WEIGHT_MIN,
            cst.DEFAULT_PEDESTRIAN_WEIGHT_MAX,
            value=current_agent.measures.measures["weight"],
            step=1.0,
            key=f"weight_{selected_id}",
            on_change=parameter_changed,
        )

    elif current_agent.agent_type.name == cst.AgentTypes.bike.name:
        bike_params = ["wheel_width", "total_length", "handlebar_length", "top_tube_length", "weight"]
        defaults_min_max_step = {
            "wheel_width": (cst.DEFAULT_WHEEL_WIDTH_MIN, cst.DEFAULT_WHEEL_WIDTH_MAX, 0.5),
            "total_length": (cst.DEFAULT_TOTAL_LENGTH_MIN, cst.DEFAULT_TOTAL_LENGTH_MAX, 1.0),
            "handlebar_length": (cst.DEFAULT_HANDLEBAR_LENGTH_MIN, cst.DEFAULT_HANDLEBAR_LENGTH_MAX, 1.0),
            "top_tube_length": (cst.DEFAULT_TOP_TUBE_LENGTH_MIN, cst.DEFAULT_TOP_TUBE_LENGTH_MAX, 1.0),
            "weight": (cst.DEFAULT_BIKE_WEIGHT_MIN, cst.DEFAULT_BIKE_WEIGHT_MAX, 1.0),
        }
        for param in bike_params:
            current_agent.measures.measures[param] = st.sidebar.slider(
                f"{param.replace('_', ' ').title()} (cm)" if param != "weight" else "Weight (kg)",
                defaults_min_max_step[param][0],
                defaults_min_max_step[param][1],
                value=current_agent.measures.measures[param],
                step=defaults_min_max_step[param][2],
                key=f"{param}_{selected_id}",
                on_change=parameter_changed,
            )


def run_tab_custom_crowd() -> None:
    """
    Provide an interactive interface for creating, managing, visualizing, and downloading a custom crowd of agents.

    Users can add or remove agents, adjust their parameters (e.g., anthropometric measures, position, rotation), and export
    the scene or data in various formats.

    Attributes
    ----------
    Sidebar:
        - Agent management:
            - Buttons to add pedestrians or bikes.
            - Dropdown to select an agent for adjustment.
            - Button to remove the selected agent.
        - Parameter adjustment:
            - Sliders for anthropometric measures (via `sliders_for_agent_parameters`).
            - Sliders for position and rotation adjustments.
        - Download options:
            - Export the scene as a PDF file.
            - Backup data in XML, JSON, or pickle formats.
    Main Page:
        - Visualization of the custom crowd using Plotly charts.
        - Message displayed if no agents are present.

    Notes
    -----
    - Users can dynamically add pedestrians or bikes to the crowd via sidebar buttons.
    - Each agent's parameters (e.g., measures, position, rotation) can be adjusted using sliders.
    - The main page displays a 2D visualization of the crowd using Plotly.
    - Download options include exporting the plot as a PDF and backing up data in XML, JSON, or pickle formats.
    """
    initialize_session_state()
    agents = st.session_state.agents

    # Sidebar: Manage Agents
    st.sidebar.header("Manage agents")
    if st.sidebar.button("Add a pedestrian"):
        add_agent(cst.AgentTypes.pedestrian)
    if st.sidebar.button("Add a bike"):
        add_agent(cst.AgentTypes.bike)

    # Sidebar: Select Agent
    if agents:
        selected_id = st.sidebar.selectbox(
            "Select agent",
            options=range(len(agents)),
            format_func=lambda x: f"Agent {x + 1}",
            key="select_agent",
        )
        current_agent = agents[selected_id]
        st.session_state.current_agent_id = selected_id

        # Remove agent button
        if st.sidebar.button("Remove selected agent"):
            remove_agent(selected_id)

        # Sidebar: adjust parameters
        st.sidebar.header("Adjust agent parameters")
        sliders_for_agent_parameters(selected_id, current_agent)

        # Sidebar: adjust position
        st.sidebar.header("Adjust Position")
        # Translation and Rotation Sliders
        current_agent.x_translation = st.sidebar.slider(
            "X-translation (cm)",
            -100.0,
            100.0,
            value=getattr(current_agent, "x_translation", 0.0),
            step=1.0,
            key=f"x_translation_{selected_id}",
            on_change=parameter_changed,
        )

        current_agent.y_translation = st.sidebar.slider(
            "Y-translation (cm)",
            -100.0,
            100.0,
            value=getattr(current_agent, "y_translation", 0.0),
            step=1.0,
            key=f"y_translation_{selected_id}",
            on_change=parameter_changed,
        )

        old_orientation = getattr(current_agent, "rotation_angle", 0.0)
        current_agent.rotation_angle = st.sidebar.slider(
            "Rotation angle (degrees)",
            -180.0,
            180.0,
            value=getattr(current_agent, "rotation_angle", 0.0),
            step=1.0,
            key=f"rotation_angle_{selected_id}",
            on_change=parameter_changed,
        )

        # Apply transformations
        delta_x = current_agent.x_translation - current_agent.get_position().x
        delta_y = current_agent.y_translation - current_agent.get_position().y
        delta_theta = current_agent.rotation_angle - old_orientation
        if st.session_state.simulation_run:
            current_agent.translate(delta_x, delta_y)
            current_agent.rotate(delta_theta)
            st.session_state.simulation_run = False

    # Main Page Visualization
    st.subheader("Visualisation")
    col1, _ = st.columns([2.0, 1])
    with col1:
        if agents:
            fig = plot.display_shape2D(agents)
            st.plotly_chart(fig)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Download plot as PDF
            st.sidebar.header("Download")

            st.sidebar.download_button(
                label="Download plot as PDF",
                data=fig.to_image(format="pdf"),
                file_name=f"scene_custom_crowd_{timestamp}.pdf",
                mime="application/pdf",
            )

            # Backup data download option
            backup_format: BackupDataType = st.sidebar.selectbox(
                "Backup Format:",
                [cst.BackupDataTypes.xml.name, cst.BackupDataTypes.json.name, cst.BackupDataTypes.pickle.name],
                format_func=lambda x: x.upper(),
                help="Choose the format for your data backup.",
            )

            crowd_dict: dict[str, dict[str, ShapeDataType | str]] = {
                f"agent{id}": {
                    "agent_type": agent.agent_type.name,
                    "shapes": agent.shapes2D.get_additional_parameters(),
                }
                for id, agent in enumerate(agents)
            }

            backup_data, mime_type = fun.get_shapes_data(backup_format, crowd_dict)

            st.sidebar.download_button(
                label=f"Download Data as {backup_format.upper()}",
                data=backup_data,
                file_name=f"custom_crowd_{backup_format}_{timestamp}.{backup_format}",
                mime=mime_type,
            )

        else:
            st.write("No agents to display.")
