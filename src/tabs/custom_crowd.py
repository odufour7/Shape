"""Custom Crowd Tab"""

from datetime import datetime

import streamlit as st

import src.utils.constants as cst
from src.classes.agents import Agent
from src.classes.measures import AgentMeasures
from src.plotting import plot
from src.utils import functions as fun


# Main function for the custom crowd tab
def main():
    """Main function for the custom crowd tab."""
    # Initialize session state for agents and current pedestrian ID
    if "agents" not in st.session_state:
        st.session_state.agents = []  # List to store pedestrian objects
    if "current_agent_id" not in st.session_state:
        st.session_state.current_agent_id = None

    # Access agents from session state
    agents = st.session_state.agents

    # Sidebar: Add a new agent
    st.sidebar.header("Manage agents")
    if st.sidebar.button("Add a pedestrian"):
        agent_measures = AgentMeasures(
            agent_type=cst.AgentTypes.pedestrian.name,
            measures={
                "sex": cst.DEFAULT_SEX,
                "bideltoid_breadth": cst.DEFAULT_BIDELTOID_BREADTH,
                "chest_depth": cst.DEFAULT_CHEST_DEPTH,
                "height": cst.DEFAULT_HEIGHT,
            },
        )
        new_agent = Agent(agent_type=cst.AgentTypes.pedestrian.name, measures=agent_measures)
        agents.append(new_agent)
        st.session_state.current_agent_id = len(agents) - 1  # Set the new pedestrian as current

    if st.sidebar.button("Add a bike"):
        agent_measures = AgentMeasures(
            agent_type=cst.AgentTypes.bike.name,
            measures={
                "wheel_width": cst.DEFAULT_WHEEL_WIDTH,
                "total_length": cst.DEFAULT_TOTAL_LENGTH,
                "handlebar_length": cst.DEFAULT_HANDLEBAR_LENGTH,
                "top_tube_length": cst.DEFAULT_TOP_TUBE_LENGTH,
            },
        )
        new_agent = Agent(agent_type=cst.AgentTypes.bike.name, measures=agent_measures)
        agents.append(new_agent)
        st.session_state.current_agent_id = len(agents) - 1  # Set the new pedestrian as current

    # Sidebar: Dropdown to select a pedestrian
    if agents:
        agent_ids = [f"Agent {i+1}" for i in range(len(agents))]
        selected_id = st.sidebar.selectbox(
            "Select Agent",
            options=range(len(agents)),
            format_func=lambda x: agent_ids[x],
            key="select_pedestrian",
        )
        # Save the currently selected pedestrian ID
        st.session_state.current_agent_id = selected_id

        # Access the currently selected pedestrian
        current_agent = agents[selected_id]

        # Sidebar: Button to remove the selected pedestrian
        if st.sidebar.button("Remove Selected Pedestrian"):
            # Remove the currently selected pedestrian
            del agents[st.session_state.current_agent_id]

            # Update the currently selected pedestrian ID
            if agents:
                st.session_state.current_agent_id = min(st.session_state.current_agent_id, len(agents) - 1)
            else:
                st.session_state.current_agent_id = None
                # rerun the file to update the sliders
                st.rerun()

        # Sidebar Sliders for Anthropometric Parameters
        st.sidebar.header("Adjust Parameters")

        if current_agent.agent_type == cst.AgentTypes.pedestrian.name:
            # Update bideltoid breadth
            new_bideltoid_breadth = st.sidebar.slider(
                "Bideltoid breadth (cm)",
                min_value=cst.MIN_BIDELTOID_BREADTH,
                max_value=cst.MAX_BIDELTOID_BREADTH,
                value=current_agent.measures.measures["bideltoid_breadth"],
                step=1.0,
                key=f"bideltoid_breadth_{selected_id}",
            )

            # Update chest depth
            new_chest_depth = st.sidebar.slider(
                "Chest depth (cm)",
                min_value=cst.MIN_CHEST_DEPTH,
                max_value=cst.MAX_CHEST_DEPTH,
                value=current_agent.measures.measures["chest_depth"],
                step=1.0,
                key=f"chest_depth_{selected_id}",
            )

            current_agent.measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian.name,
                measures={
                    "sex": cst.DEFAULT_SEX,
                    "bideltoid_breadth": new_bideltoid_breadth,
                    "chest_depth": new_chest_depth,
                    "height": cst.DEFAULT_HEIGHT,
                },
            )
        if current_agent.agent_type == cst.AgentTypes.bike.name:
            wheel_width = st.sidebar.slider(
                "Wheel width (cm)",
                min_value=cst.MIN_WHEEL_WIDTH,
                max_value=cst.MAX_WHEEL_WIDTH,
                value=current_agent.measures.measures["wheel_width"],
                step=0.5,
            )
            total_length = st.sidebar.slider(
                "Total length (cm)",
                min_value=cst.MIN_TOTAL_LENGTH,
                max_value=cst.MAX_TOTAL_LENGTH,
                value=current_agent.measures.measures["total_length"],
                step=1.0,
            )
            handlebar_length = st.sidebar.slider(
                "Handlebar length (cm)",
                min_value=cst.MIN_HANDLEBAR_LENGTH,
                max_value=cst.MAX_HANDLEBAR_LENGTH,
                value=current_agent.measures.measures["handlebar_length"],
                step=1.0,
            )
            top_tube_length = st.sidebar.slider(
                "Top tube length (cm)",
                min_value=cst.MIN_TOP_TUBE_LENGTH,
                max_value=cst.MAX_TOP_TUBE_LENGTH,
                value=current_agent.measures.measures["top_tube_length"],
                step=1.0,
            )
            current_agent.measures = AgentMeasures(
                agent_type=cst.AgentTypes.bike.name,
                measures={
                    "wheel_width": wheel_width,
                    "total_length": total_length,
                    "handlebar_length": handlebar_length,
                    "top_tube_length": top_tube_length,
                },
            )

        # Input fields for translation and rotation
        # In Python due to its dynamic nature, which allows adding attributes to objects at runtime.
        current_agent.x_translation = st.sidebar.slider(
            "X-Translation (cm):",
            min_value=-100.0,
            max_value=100.0,
            value=getattr(current_agent, "x_translation", 0.0),
            step=1.0,
            key=f"x_translation_{selected_id}",
        )

        current_agent.y_translation = st.sidebar.slider(
            "Y-Translation (cm):",
            min_value=-100.0,
            max_value=100.0,
            value=getattr(current_agent, "y_translation", 0.0),
            step=1.0,
            key=f"y_translation_{selected_id}",
        )

        current_agent.rotation_angle = st.sidebar.slider(
            "Rotation Angle (degrees):",
            min_value=-180.0,
            max_value=180.0,
            value=getattr(current_agent, "rotation_angle", 0.0),
            step=1.0,
            key=f"rotation_angle_{selected_id}",
        )

        # Update shape transformations
        current_agent.translate(current_agent.x_translation, current_agent.y_translation)
        current_agent.rotate(current_agent.rotation_angle)

    # Main Page Content: Plot all pedestrians
    st.subheader("Visualisation")
    col1, _ = st.columns([2.0, 1])  # Adjust proportions as needed
    with col1:
        if agents:
            fig = plot.display_shape2D(agents)  # Pass the list of all pedestrians to the plot function
            st.plotly_chart(fig)
        else:
            st.write("No pedestrians to display.")

    # Streamlit button in the sidebar to download the graph in PDF format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.sidebar.header("Download")
    st.sidebar.download_button(
        label="Download plot as PDF",
        data=fig.to_image(format="pdf"),
        file_name=f"scene_custom_crowd_{timestamp}.pdf",
        mime="application/pdf",
    )
    # Create a select box for format selection
    backup_data_type = st.sidebar.selectbox(
        "Select backup format:",
        options=[cst.BackupDataTypes.json.name, cst.BackupDataTypes.xml.name, cst.BackupDataTypes.pickle.name],
        format_func=lambda x: x.upper(),
        help="Choose the format for your data backup.",
    )
    # Add a download button
    filename = f"custom_crowd_{backup_data_type}_{timestamp}.{backup_data_type}"
    crowd_dict = {
        f"agent{id_agent}": {"type": agent.agent_type, "shapes": agent.shapes2D.get_additional_parameters()}
        for id_agent, agent in enumerate(agents)
    }

    data, mime_type = fun.get_shapes_data(backup_data_type, crowd_dict)
    st.sidebar.download_button(
        label=f"Download data as {backup_data_type.upper()}",
        data=data,
        file_name=filename,
        mime=mime_type,
    )


def run_tab_custom_crowd() -> None:
    """Execute the main function for the custom crowd tab."""
    main()
