"""Custom Crowd Tab."""

from datetime import datetime

import streamlit as st

import src.utils.constants as cst
from src.classes.agents import Agent
from src.classes.measures import AgentMeasures
from src.plotting import plot
from src.utils import functions as fun
from src.utils.typing_custom import BackupDataType, Sex


# Helper function to initialize session state
def initialize_session_state() -> None:
    """Initialize the session state for agents and current agent ID.

    This function checks if the session state contains the keys 'agents' and
    'current_agent_id'. If not, it initializes 'agents' as an empty list and
    'current_agent_id' as None.

    Returns
    -------
        None
    """
    if "agents" not in st.session_state:
        st.session_state.agents = []
    if "current_agent_id" not in st.session_state:
        st.session_state.current_agent_id = None


# Helper function to add a new agent
def add_agent(agent_type: cst.AgentTypes) -> None:
    """Add a new agent of the specified type to the session state.

    Parameters
    ----------
    agent_type : AgentType
        The type of agent to be added. It should be one of the predefined agent types.

    Returns
    -------
    None
    """
    default_measures: dict[cst.AgentTypes, dict[str, float | Sex]] = {
        cst.AgentTypes.pedestrian: {
            "sex": cst.DEFAULT_SEX,
            "bideltoid_breadth": cst.DEFAULT_BIDELTOID_BREADTH,
            "chest_depth": cst.DEFAULT_CHEST_DEPTH,
            "height": cst.DEFAULT_HEIGHT,
        },
        cst.AgentTypes.bike: {
            "wheel_width": cst.DEFAULT_WHEEL_WIDTH,
            "total_length": cst.DEFAULT_TOTAL_LENGTH,
            "handlebar_length": cst.DEFAULT_HANDLEBAR_LENGTH,
            "top_tube_length": cst.DEFAULT_TOP_TUBE_LENGTH,
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
    """Remove an agent from the session state by its ID.

    Parameters
    ----------
    selected_id : int
        The ID of the agent to be removed.

    Returns
    -------
    None

    Side Effects
    ------------
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


# Helper function to create sliders easily
def create_slider(label: str, min_val: float | int, max_val: float | int, value: float | int, step: int, key: str) -> float | int:
    """
    Create a slider widget in the Streamlit sidebar.

    Parameters
    ----------
    label :str
        The label displayed next to the slider.
    min_val : float | int
        The minimum value of the slider.
    max_val : float | int
        The maximum value of the slider.
    value : float | int
        The initial value of the slider.
    step : int
        The step size between values.
    key : str
        An optional string to use as the unique key for the widget.

    Returns
    -------
    float | int
        The current value of the slider.
    """
    return st.sidebar.slider(label, min_val, max_val, value=value, step=step, key=key)


# Main Streamlit App Function
def main() -> None:
    """
    Manage and visualize agents in a custom crowd simulation.

    This function initializes the session state, manages the addition and removal of agents,
    adjusts parameters for each agent, and provides visualization and download options.

    Features
    --------
    - Add and remove agents (pedestrians and bikes) via sidebar buttons.
    - Select an agent from the sidebar to adjust its parameters.
    - Adjust parameters specific to pedestrians (bideltoid breadth, chest depth) and bikes
      (wheel width, total length, handlebar length, top tube length).
    - Adjust translation (x, y) and rotation angle for the selected agent.
    - Visualize the current state of agents on the main page.
    - Download the plot as a PDF.
    - Backup data in various formats (JSON, XML, Pickle).

    Note
    ----
    - Assumes the existence of certain constants and functions (e.g., `cst`, `create_slider`,
      `plot.display_shape2D`, `fun.get_shapes_data`).
    - Assumes the existence of certain constants and functions (e.g., `cst`, `create_slider`,
      `plot.display_shape2D`, `fun.get_shapes_data`).

    """
    initialize_session_state()
    agents = st.session_state.agents

    # Sidebar: Manage Agents
    st.sidebar.header("Manage Agents")
    if st.sidebar.button("Add a Pedestrian"):
        add_agent(cst.AgentTypes.pedestrian)
    if st.sidebar.button("Add a Bike"):
        add_agent(cst.AgentTypes.bike)

    # Sidebar: Select Agent
    if agents:
        selected_id = st.sidebar.selectbox(
            "Select Agent",
            options=range(len(agents)),
            format_func=lambda x: f"Agent {x + 1}",
            key="select_agent",
        )
        current_agent = agents[selected_id]
        st.session_state.current_agent_id = selected_id

        # Remove agent button
        if st.sidebar.button("Remove Selected Agent"):
            remove_agent(selected_id)

        # Sidebar: Adjust Parameters
        st.sidebar.header("Adjust Parameters")

        if current_agent.agent_type == cst.AgentTypes.pedestrian.name:
            current_agent.measures.measures["bideltoid_breadth"] = create_slider(
                "Bideltoid breadth (cm)",
                cst.DEFAULT_BIDELTOID_BREADTH_MIN,
                cst.DEFAULT_BIDELTOID_BREADTH_MAX,
                current_agent.measures.measures["bideltoid_breadth"],
                1,
                f"bideltoid_{selected_id}",
            )

            current_agent.measures.measures["chest_depth"] = create_slider(
                "Chest depth (cm)",
                cst.DEFAULT_CHEST_DEPTH_MIN,
                cst.DEFAULT_CHEST_DEPTH_MAX,
                current_agent.measures.measures["chest_depth"],
                1,
                f"chest_{selected_id}",
            )

        elif current_agent.agent_type == cst.AgentTypes.bike.name:
            bike_params = ["wheel_width", "total_length", "handlebar_length", "top_tube_length"]
            defaults_min_max_step = {
                "wheel_width": (cst.DEFAULT_WHEEL_WIDTH_MIN, cst.DEFAULT_WHEEL_WIDTH_MAX, 0.5),
                "total_length": (cst.DEFAULT_TOTAL_LENGTH_MIN, cst.DEFAULT_TOTAL_LENGTH_MAX, 1.0),
                "handlebar_length": (cst.DEFAULT_HANDLEBAR_LENGTH_MIN, cst.DEFAULT_HANDLEBAR_LENGTH_MAX, 1.0),
                "top_tube_length": (cst.DEFAULT_TOP_TUBE_LENGTH_MIN, cst.DEFAULT_TOP_TUBE_LENGTH_MAX, 1.0),
            }

            for param in bike_params:
                min_v, max_v, step_v = defaults_min_max_step[param]
                current_agent.measures.measures[param] = create_slider(
                    f"{param.replace('_', ' ').title()} (cm)",
                    min_v,
                    max_v,
                    current_agent.measures.measures[param],
                    int(step_v),
                    f"{param}_{selected_id}",
                )

        # Translation and Rotation Sliders
        current_agent.x_translation = create_slider(
            "X-Translation (cm)", -100.0, 100.0, getattr(current_agent, "x_translation", 0.0), 1, f"x_translation_{selected_id}"
        )

        current_agent.y_translation = create_slider(
            "Y-Translation (cm)", -100.0, 100.0, getattr(current_agent, "y_translation", 0.0), 1, f"y_translation_{selected_id}"
        )

        current_agent.rotation_angle = create_slider(
            "Rotation Angle (degrees)",
            -180.0,
            180.0,
            getattr(current_agent, "rotation_angle", 0.0),
            1,
            f"rotation_angle_{selected_id}",
        )

        # Apply transformations
        current_agent.translate(current_agent.x_translation, current_agent.y_translation)
        current_agent.rotate(current_agent.rotation_angle)

    # Main Page Visualization
    st.subheader("Visualization")
    col1, _ = st.columns([2.0, 1])
    with col1:
        if agents:
            fig = plot.display_shape2D(agents)
            st.plotly_chart(fig)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Download plot as PDF
            st.sidebar.header("Download")

            pdf_data = fig.to_image(format="pdf")

            st.sidebar.download_button(
                label="Download Plot as PDF",
                data=pdf_data,
                file_name=f"scene_custom_crowd_{timestamp}.pdf",
                mime="application/pdf",
            )

            # Backup data download option
            backup_format: BackupDataType = st.sidebar.selectbox(
                "Backup Format:",
                [cst.BackupDataTypes.json.name, cst.BackupDataTypes.xml.name, cst.BackupDataTypes.pickle.name],
                format_func=lambda x: x.upper(),
                help="Choose the format for your data backup.",
            )

            crowd_dict = {
                f"agent{id}": {
                    "agent_type": agent.agent_type,
                    "shapes": agent.shapes2D.get_additional_parameters(),
                }
                for id, agent in enumerate(agents)
            }

            backup_data, mime_type = fun.get_shapes_data(backup_format, crowd_dict)

            filename_backup = f"custom_crowd_{backup_format}_{timestamp}.{backup_format}"

            st.sidebar.download_button(
                label=f"Download Data as {backup_format.upper()}",
                data=backup_data,
                file_name=filename_backup,
                mime=mime_type,
            )

        else:
            st.write("No agents to display.")


def run_tab_custom_crowd() -> None:
    """Execute the main function for the custom crowd tab."""
    main()
