"""Custom crowd tab."""

from datetime import datetime

import streamlit as st

import configuration.backup.crowd_to_dict as fun_dict
import configuration.backup.crowd_to_zip_and_reverse as fun_zip
import configuration.backup.dict_to_xml_and_reverse as fun_xml
import configuration.utils.constants as cst
import streamlit_app.utils.constants as cst_app
from configuration.models.agents import Agent
from configuration.models.crowd import Crowd
from configuration.models.measures import AgentMeasures
from configuration.utils.typing_custom import Sex
from streamlit_app.plot import plot


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


def parameter_not_changed() -> None:
    """Update the Streamlit session state to indicate that a simulation should not be run."""
    st.session_state.simulation_run = False


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
            "sex": cst_app.DEFAULT_SEX,
            "bideltoid_breadth": cst.CrowdStat["male_bideltoid_breadth_mean"],
            "chest_depth": cst.CrowdStat["male_chest_depth_mean"],
            "height": cst_app.DEFAULT_PEDESTRIAN_HEIGHT,
            "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
        },
        cst.AgentTypes.bike: {
            "wheel_width": cst.CrowdStat["wheel_width_mean"],
            "total_length": cst.CrowdStat["total_length_mean"],
            "handlebar_length": cst.CrowdStat["handlebar_length_mean"],
            "top_tube_length": cst.CrowdStat["top_tube_length_mean"],
            "weight": cst.DEFAULT_BIKE_WEIGHT,
        },
    }

    agent_measures = AgentMeasures(
        agent_type=agent_type,
        measures=default_measures[agent_type],
    )
    new_agent = Agent(agent_type=agent_type, measures=agent_measures)
    new_agent.rotate(-90.0)  # Rotate the agent to face the positive x-axis
    new_agent_position = new_agent.get_position()
    new_agent.translate(new_agent_position.x, new_agent_position.y)
    st.session_state.agents.append(new_agent)
    st.session_state.current_agent_id = len(st.session_state.agents) - 1
    parameter_not_changed()


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
            cst.CrowdStat["male_bideltoid_breadth_min"],
            cst.CrowdStat["male_bideltoid_breadth_max"],
            value=current_agent.measures.measures["bideltoid_breadth"],
            step=1.0,
            key=f"bideltoid_{selected_id}",
            on_change=parameter_changed,
        )
        current_agent.measures.measures["chest_depth"] = st.sidebar.slider(
            "Chest depth (cm)",
            cst.CrowdStat["male_chest_depth_min"],
            cst.CrowdStat["male_chest_depth_max"],
            value=current_agent.measures.measures["chest_depth"],
            step=1.0,
            key=f"chest_{selected_id}",
            on_change=parameter_changed,
        )
        current_agent.measures.measures["weight"] = st.sidebar.slider(
            "Weight (kg)",
            cst.CrowdStat["pedestrian_weight_min"],
            cst.CrowdStat["pedestrian_weight_max"],
            value=current_agent.measures.measures["weight"],
            step=1.0,
            key=f"weight_{selected_id}",
            on_change=parameter_changed,
        )
        agent_measures = AgentMeasures(
            agent_type=cst.AgentTypes.pedestrian,
            measures={
                "sex": current_agent.measures.measures["sex"],
                "bideltoid_breadth": current_agent.measures.measures["bideltoid_breadth"],
                "chest_depth": current_agent.measures.measures["chest_depth"],
                "height": cst_app.DEFAULT_PEDESTRIAN_HEIGHT,
                "weight": cst.DEFAULT_PEDESTRIAN_WEIGHT,
            },
        )
        current_agent.measures = agent_measures

    elif current_agent.agent_type.name == cst.AgentTypes.bike.name:
        bike_params = ["wheel_width", "total_length", "handlebar_length", "top_tube_length", "weight"]
        defaults_min_max_step = {
            "wheel_width": (cst.CrowdStat["wheel_width_min"], cst.CrowdStat["wheel_width_max"], 0.5),
            "total_length": (cst.CrowdStat["total_length_min"], cst.CrowdStat["total_length_max"], 1.0),
            "handlebar_length": (cst.CrowdStat["handlebar_length_min"], cst.CrowdStat["handlebar_length_max"], 1.0),
            "top_tube_length": (cst.CrowdStat["top_tube_length_min"], cst.CrowdStat["top_tube_length_max"], 1.0),
            "weight": (cst.CrowdStat["bike_weight_min"], cst.CrowdStat["bike_weight_max"], 1.0),
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
        agent_measures = AgentMeasures(
            agent_type=cst.AgentTypes.bike,
            measures={
                "wheel_width": current_agent.measures.measures["wheel_width"],
                "total_length": current_agent.measures.measures["total_length"],
                "handlebar_length": current_agent.measures.measures["handlebar_length"],
                "top_tube_length": current_agent.measures.measures["top_tube_length"],
                "weight": cst.DEFAULT_BIKE_WEIGHT,
            },
        )
        current_agent.measures = agent_measures


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
            - Backup data in XML, or pickle formats.
    Main Page:
        - Visualization of the custom crowd using Plotly charts.
        - Message displayed if no agents are present.

    Notes
    -----
    - Users can dynamically add pedestrians or bikes to the crowd via sidebar buttons.
    - Each agent's parameters (e.g., measures, position, rotation) can be adjusted using sliders.
    - The main page displays a 2D visualization of the crowd using Plotly.
    - Download options include exporting the plot as a PDF and backing up data in XML, or pickle formats.
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
        if st.session_state.simulation_run:
            delta_x = current_agent.x_translation - current_agent.get_position().x
            delta_y = current_agent.y_translation - current_agent.get_position().y
            delta_theta = current_agent.rotation_angle - current_agent.get_agent_orientation()
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

            # Download all files as ZIP
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            current_crowd: Crowd = Crowd(agents=agents)

            # check if the agent type are only pedestrians :
            if all(agent.agent_type == cst.AgentTypes.pedestrian for agent in agents):
                filename = f"crowd2D_{timestamp}.zip"

                zip_buffer = fun_zip.write_crowd_data_to_zip(current_crowd)

                # Add download button for the ZIP file
                st.sidebar.download_button(
                    label="Download all files as ZIP",
                    data=zip_buffer,
                    file_name=filename,
                    mime="application/zip",
                )
            else:
                filename = f"crowd2D_{timestamp}.xml"

                data_dict = fun_dict.get_light_agents_params(current_crowd)
                data = fun_xml.save_light_agents_params_dict_to_xml(data_dict)

                st.sidebar.download_button(
                    label="Download as XML",
                    data=data,
                    file_name=filename,
                    mime="application/xml",
                )

        else:
            st.write("No agents to display.")
