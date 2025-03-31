"""Contains functions to plot the geometric shapes of the pedestrian and the crowd."""

import logging
from typing import Literal

import cmcrameri as cram
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyvista as pv
from matplotlib.colors import Normalize
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
from numpy.typing import NDArray
from shapely.geometry import MultiPolygon, Polygon
from streamlit.delta_generator import DeltaGenerator

import shapes.utils.functions as fun
from shapes.classes.agents import Agent
from shapes.classes.crowd import Crowd

# plt.rcParams.update(
#     {
#         "text.usetex": True,
#         "font.family": "serif",
#         "font.serif": ["Computer Modern Roman"],
#         "font.size": 23,
#         "text.latex.preamble": r"\usepackage{amsmath}",
#         "figure.dpi": 300,
#     }
# )


def display_shape2D(agents: list[Agent]) -> go.Figure:
    """
    Visualize 2D geometric shapes of agents using Plotly.

    This function generates a 2D Plotly figure that displays the geometric shapes
    of agents, which can be either `Polygon` or `MultiPolygon` geometries.

    Parameters
    ----------
    agents : list[Agent]
        A list of `Agent` objects. Each `Agent` must have a 2D geometric shape accessible
        via the `shapes2D.get_geometric_shape()` method. The geometric shape must be
        either a `Polygon` or a `MultiPolygon`.

    Returns
    -------
    go.Figure
        A Plotly `Figure` object displaying the 2D shapes of the agents.

    Notes
    -----
    - If an agent's shape is a `Polygon`, it is directly plotted with its exterior boundary.
    - If an agent's shape is a `MultiPolygon`, each individual polygon in the collection
      is plotted separately.
    - The centroid of each shape (or collection of shapes) is computed and annotated
      with the corresponding agent's ID.
    """
    # Initialize a Plotly figure
    fig = go.Figure()

    # Add each agent's shape to the plot
    for id_agent, agent in enumerate(agents):
        id_agent += 1
        geometric_agent = agent.shapes2D.get_geometric_shape()
        if isinstance(geometric_agent, Polygon):
            x, y = geometric_agent.exterior.xy
            fig.add_trace(
                go.Scatter(
                    x=np.array(x),
                    y=np.array(y),
                    fill="toself",
                    mode="lines",
                    line={"color": "black", "width": 1},
                    fillcolor="rgba(255, 0, 0, 0.5)",
                    name=f"agent {id_agent}",
                )
            )

            # Add pedestrian ID as annotation
            centroid_x = np.mean(x)
            centroid_y = np.mean(y)
            fig.add_annotation(
                x=centroid_x,
                y=centroid_y,
                text=f"agent {id_agent}",
                showarrow=False,
                font={"size": 12, "color": "white"},
                align="center",
            )

        # If the agent's shape is a MultiPolygon, plot each polygon separately
        elif isinstance(geometric_agent, MultiPolygon):
            for polygon in geometric_agent.geoms:
                x, y = polygon.exterior.xy
                fig.add_trace(
                    go.Scatter(
                        x=np.array(x),
                        y=np.array(y),
                        fill="toself",
                        mode="lines",
                        line={"color": "black", "width": 1},
                        fillcolor="rgba(255, 0, 0, 0.5)",
                    )
                )

            # Add pedestrian ID as annotation
            centroid_x = np.mean([np.mean(polygon.exterior.xy[0]) for polygon in geometric_agent.geoms])
            centroid_y = np.mean([np.mean(polygon.exterior.xy[1]) for polygon in geometric_agent.geoms])
            fig.add_annotation(
                x=centroid_x,
                y=centroid_y,
                text=f"agent {id_agent}",
                showarrow=False,
                font={"size": 12, "color": "white"},
                align="center",
            )

    # Set layout properties
    fig.update_layout(
        xaxis_title="X [cm]",
        yaxis_title="Y [cm]",
        xaxis={"scaleanchor": "y", "showgrid": False, "title_standoff": 15},
        yaxis={"showgrid": False, "title_standoff": 15},
        showlegend=False,
        margin={"l": 50, "r": 50, "t": 50, "b": 50},
        width=550,
        height=550,
    )

    return fig


def display_body3D_orthogonal_projection(agent: Agent, extra_info: tuple[DeltaGenerator, DeltaGenerator]) -> Figure:
    """
    Visualize the orthogonal projection of a pedestrian's 3D body using Matplotlib.

    This function generates a 2D orthogonal projection of a pedestrian's 3D body.
    The projection is based on the agent's 2D shapes at various heights, which are
    color-coded using a colormap to represent height values.

    Parameters
    ----------
    agent : Agent
        The `Agent` object containing the 3D shapes and measures of the pedestrian.
        The 3D shapes must be accessible via `agent.shapes3D.shapes`, where each key
        represents a height (as a string) and its value is a `MultiPolygon` object.
    extra_info : tuple[DeltaGenerator, DeltaGenerator]
        A tuple containing:
        - A `DeltaGenerator` object for updating the progress bar.
        - A string or additional information to display alongside the progress bar.

    Returns
    -------
    Figure
        A Matplotlib `Figure` object displaying the orthogonal projection of the pedestrian's body.

    Raises
    ------
    ValueError
        If `agent.shapes3D` or `agent.shapes3D.shapes` is `None`.
        If any shape in `agent.shapes3D.shapes` is not a `MultiPolygon`.
    """
    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    # Create a ScalarMappable object for color mapping
    sm = plt.cm.ScalarMappable(
        cmap="coolwarm",
        norm=Normalize(vmin=0, vmax=max(agent.shapes3D.shapes.keys(), key=float)),
    )

    # Initialize a Matplotlib figure
    fig, ax = plt.subplots(figsize=(11, 11))

    # Normalize heights for color mapping
    min_height = min(agent.shapes3D.shapes.keys(), key=float)
    max_height = max(agent.shapes3D.shapes.keys(), key=float)

    # Plot each polygon at different heights
    for height in sorted(agent.shapes3D.shapes.keys(), key=float):
        multi_polygon = agent.shapes3D.shapes[height]
        if not isinstance(multi_polygon, MultiPolygon):
            raise ValueError("multi_polygon is not a MultiPolygon")
        proportion_completed = (height - min_height) / (max_height - min_height)
        fun.update_progress_bar(extra_info[0], extra_info[1], proportion_completed)
        for polygon in multi_polygon.geoms:
            x, y = polygon.exterior.xy
            ax.plot(x, y, color=sm.to_rgba(np.array([height])), alpha=0.6, linewidth=2)

    # Add a colorbar with inverted orientation (red at top)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.2)

    # Set colorbar properties
    plt.colorbar(sm, cax=cax, label="Height [cm]")

    # Set plot properties
    ax.set_title(f"Orthogonal projection of a {agent.measures.measures['sex']}")
    ax.margins(0)
    ax.set_aspect("equal")
    ax.set_xlabel("X [cm]")
    ax.set_ylabel("Y [cm]")
    plt.tight_layout()

    return fig


def compute_range(agent: Agent, axis: Literal["x", "y"]) -> float:
    """
    Compute the range (maximum - minimum) of coordinates along a given axis for an agent's 3D shapes.

    Parameters
    ----------
    agent : Agent
        The agent object containing 3D shape information.
    axis : Literal["x", "y"]
        The axis along which to compute the range.

    Returns
    -------
    float
        The range (maximum - minimum) of coordinates along the specified axis.

    Raises
    ------
    ValueError
        If the axis is not 'x' or 'y', if agent.shapes3D or agent.shapes3D.shapes is None,
        or if any shape in agent.shapes3D.shapes is not a MultiPolygon.
    """
    # Check if axis is either "x" or "y"
    if axis not in ("x", "y"):
        raise ValueError("Axis must be 'x' or 'y'")

    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    # Put the coordinates in a list
    coord_index = 0 if axis == "x" else 1
    coordinates: list[float] = []
    for multi_polygon in agent.shapes3D.shapes.values():
        # Check if multi_polygon is of type MultiPolygon
        if not isinstance(multi_polygon, MultiPolygon):
            raise ValueError("multi_polygon is not a MultiPolygon")

        # Extract coordinates for the given axis from all polygons
        coordinates.extend(coord[coord_index] for polygon in multi_polygon.geoms for coord in polygon.exterior.coords)

    # Compute the range of values (maximum-minimum)
    xy_range: float = np.ptp(coordinates)
    return xy_range


def display_body3D_polygons(agent: Agent, extra_info: tuple[DeltaGenerator, DeltaGenerator]) -> go.Figure:
    """
    Display a 3D representation of an agent body from the polygons that constitute it.

    This function creates a 3D representation of an agent's body by plotting polygons
    at different heights. The polygons are color-coded based on the agent's height and sex.

    Parameters
    ----------
    agent : Agent
        The agent object containing 3D shapes (agent.shapes3D) and associated measurements.
    extra_info : tuple[DeltaGenerator, DeltaGenerator]
        A tuple containing a progress bar object and a status message object
        used for updating progress during visualization.

    Returns
    -------
    go.Figure
        A Plotly figure object representing the 3D body polygons.

    Raises
    ------
    ValueError
        If agent.shapes3D or agent.shapes3D.shapes is None, or if any shape
        in agent.shapes3D.shapes is not a MultiPolygon.

    Examples
    --------
    >>> agent = Agent(...)  # Agent with valid 3D shapes
    >>> progress_bar, status_message = st.progress(0), st.empty()
    >>> fig = display_body3D_polygons(agent, (progress_bar, status_message))
    >>> st.plotly_chart(fig)
    """
    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    # Initialize a Plotly figure
    fig = go.Figure()

    # Normalize heights for color mapping
    min_height = min(agent.shapes3D.shapes.keys(), key=float)
    max_height = max(agent.shapes3D.shapes.keys(), key=float)

    # Add each polygon to the 3D plot
    for height in sorted(agent.shapes3D.shapes.keys(), key=float):
        multi_polygon = agent.shapes3D.shapes[height]

        # Check if multi_polygon is a MultiPolygon object
        if not isinstance(multi_polygon, MultiPolygon):
            raise ValueError("multi_polygon is not a MultiPolygon")

        # Normalize height for color scale
        normalized_height = (height - min_height) / (max_height - min_height)  # Normalize height for color scale

        # Update progress bar
        fun.update_progress_bar(extra_info[0], extra_info[1], normalized_height)

        # Assign color based on normalized height
        if agent.measures.measures["sex"] == "female":
            # Gradient from green to red
            color = f"rgba(255, {int(205 * (normalized_height))}, {int(205 * (1 - normalized_height))}, 0.8)"
        else:
            # Gradient from blue to red
            color = f"rgba({int(205 * (1 - normalized_height))}, {int(205 * (normalized_height))}, 255, 0.8)"

        # Plot each polygon
        for polygon in multi_polygon.geoms:
            x, y = polygon.exterior.xy
            fig.add_trace(
                go.Scatter3d(
                    x=np.array(x),
                    y=np.array(y),
                    z=np.full_like(x, height),
                    mode="lines",
                    line={"width": 2, "color": color},
                )
            )

    # Determine the maximum range for equal scaling
    x_range = compute_range(agent, axis="x")
    y_range = compute_range(agent, axis="y")
    z_range = max_height - min_height
    max_range = max(x_range, y_range, z_range)

    # Set layout properties
    fig.update_layout(
        scene={
            "xaxis_title": "X [cm]",
            "yaxis_title": "Y [cm]",
            "zaxis_title": "Height [cm]",
            "aspectmode": "manual",
            "aspectratio": {
                "x": x_range / max_range,
                "y": y_range / max_range,
                "z": z_range / max_range,
            },
        },
        showlegend=False,
        width=500,
        height=900,
        scene_camera={"eye": {"x": 1.5, "y": 0.4, "z": 0.5}},
    )

    return fig


def display_body3D_mesh(agent: Agent, extra_info: tuple[DeltaGenerator, DeltaGenerator, int]) -> go.Figure:
    """
    Draw a continuous 3D mesh connecting contours at different heights.

    This function generates a smooth 3D mesh visualization of an agent by connecting shape contours
    at various heights using Plotly's Mesh3d. It fills missing triangles and smooths the mesh surface
    for improved visualization.

    Parameters
    ----------
    agent : Agent
        An instance of the Agent class containing 3D shape data (agent.shapes3D).
    extra_info : tuple[DeltaGenerator, DeltaGenerator, int]
        A tuple containing:
        - DeltaGenerator: Streamlit object for updating the progress bar.
        - DeltaGenerator: Streamlit object for displaying status messages.
        - int: Precision level used to reduce the number of processed heights.

    Returns
    -------
    go.Figure
        A Plotly Figure object displaying the generated 3D mesh.

    Raises
    ------
    ValueError
        If agent.shapes3D or agent.shapes3D.shapes is None.

    Notes
    -----
    - The function reduces the number of vertices by sampling heights based on the precision level.
    - It uses a different color scale for male (viridis) and female (inferno) agents.
    - The mesh is filled to close holes and filtered to remove artifacts below a certain height threshold.
    - The resulting 3D plot is scaled to maintain equal aspect ratios across all axes.

    Examples
    --------
    >>> agent = Agent(...)  # Agent with valid 3D shapes
    >>> progress_bar, status_message = st.progress(0), st.empty()
    >>> precision = 5
    >>> fig = display_body3D_mesh(agent, (progress_bar, status_message, precision))
    >>> st.plotly_chart(fig)
    """
    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    # Extract every nth height to reduce the number of vertices
    precision = extra_info[2]
    new_body: dict[float, MultiPolygon] = {
        height: multi_polygon for idx, (height, multi_polygon) in enumerate(agent.shapes3D.shapes.items()) if idx % precision == 0
    }
    logging.info("Number of layers: %d", len(new_body))

    # Sort the heights in descending order
    sorted_heights = np.array(sorted(new_body.keys(), reverse=True))

    # Initialize arrays to store vertices and triangles
    all_points: NDArray[np.float64] = np.empty((0, 3), dtype=float)
    all_triangles: NDArray[np.int64] = np.empty((0, 3), dtype=int)

    # Loop through consecutive heights and connect contours with triangular meshes
    for h_idx in range(len(sorted_heights) - 1):
        # Update progress bar
        percent_completed = (sorted_heights[0] - sorted_heights[h_idx] - sorted_heights[-1]) / (
            sorted_heights[0] - sorted_heights[-1]
        )
        fun.update_progress_bar(extra_info[0], extra_info[1], percent_completed)

        # Extract high and low contours for the current height pair
        height_high, height_low = sorted_heights[h_idx], sorted_heights[h_idx + 1]
        high_contours: MultiPolygon = new_body[height_high]
        low_contours: MultiPolygon = new_body[height_low]

        # Loop through high contours and connect them with low contours
        for polygon_high in high_contours.geoms:
            # Extract coordinates for high and low contours
            x_high, y_high = polygon_high.exterior.xy
            x_high, y_high = np.array(x_high), np.array(y_high)
            z_high = np.full_like(x_high, height_high)

            x_low, y_low = fun.extract_coordinates(low_contours)
            z_low = np.full_like(x_low, height_low)

            # Append high and low contours to the vertices array
            start_idx_high = all_points.shape[0]
            points_high: NDArray[np.float64] = np.column_stack((x_high, y_high, z_high))
            all_points = np.vstack((all_points, points_high))

            start_idx_low = all_points.shape[0]
            points_low = np.column_stack((x_low, y_low, z_low))
            all_points = np.vstack((all_points, points_low))

            # Connect high and low contours with triangular meshes
            for idx in range(len(x_high) - 1):
                # Find the nearest vertex in the low contour
                nearest_idx = np.argmin((x_low - x_high[idx]) ** 2 + (y_low - y_high[idx]) ** 2)
                # Triangle 1: two vertices from high contour and one from low contour
                triangle1 = np.column_stack(
                    (
                        start_idx_high + idx,
                        start_idx_high + idx + 1,
                        start_idx_low + nearest_idx,
                    )
                )
                all_triangles = np.vstack((all_triangles, triangle1))
                # Triangle 2: one vertex from high contour and two from low contour
                triangle2 = np.column_stack(
                    (
                        start_idx_high + idx + 1,
                        start_idx_low + nearest_idx,
                        start_idx_low + (nearest_idx + 1) % len(x_low),
                    )
                )
                all_triangles = np.vstack((all_triangles, triangle2))

    # Fill holes in the mesh and remove triangles associated with the last layer of vertices
    faces = np.column_stack((np.full(len(all_triangles), 3), all_triangles)).flatten()
    mesh_pv = pv.PolyData(all_points, faces)
    try:
        filled_mesh_pv = mesh_pv.fill_holes(5.0)
        points_filled = filled_mesh_pv.points
        faces_filled = filled_mesh_pv.faces.reshape(-1, 4)[:, 1:]
        all_triangles_filled = faces_filled
    except (ValueError, RuntimeError) as e:
        logging.info("Error filling holes: %s", e)
        all_triangles_filled = all_triangles

    # Filter the mesh by removing vertices and triangles below a certain threshold
    min_height = min(agent.shapes3D.shapes.keys())
    points_filled, all_triangles_filled = fun.filter_mesh_by_z_threshold(
        points_filled, all_triangles_filled, z_threshold=min_height + 0.1
    )

    # Normalize the height values for color mapping
    color_scale_name = "viridis" if agent.measures.measures["sex"] == "male" else "inferno"
    norm = Normalize(vmin=np.min(points_filled[:, 2]), vmax=np.max(points_filled[:, 2]))
    colorscale_values = norm(points_filled[:, 2])
    colorscale_values = plt.cm.get_cmap(color_scale_name)(colorscale_values)[:, :3]
    vertex_colors = [f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})" for r, g, b in colorscale_values]

    logging.info("Plotting...")

    # Create a Plotly figure with the filled mesh
    fig = go.Figure(
        data=[
            go.Mesh3d(
                x=points_filled[:, 0],
                y=points_filled[:, 1],
                z=points_filled[:, 2],
                i=all_triangles_filled[:, 0],
                j=all_triangles_filled[:, 1],
                k=all_triangles_filled[:, 2],
                facecolor=vertex_colors,
                opacity=1.0,
                colorscale=color_scale_name,
                intensity=points_filled[:, 2],
                showscale=False,
            )
        ]
    )

    # Determine the maximum range for equal scaling
    x_range = np.ptp(points_filled[:, 0])
    y_range = np.ptp(points_filled[:, 1])
    z_range = np.ptp(points_filled[:, 2])
    max_range = max(x_range, y_range, z_range)

    # Set layout properties
    fig.update_layout(
        title=f"3D body representation of a {agent.measures.measures['sex']} with a mesh",
        scene={
            "xaxis_title": "X [cm]",
            "yaxis_title": "Y [cm]",
            "zaxis_title": "Height [cm]",
            "aspectmode": "manual",
            "aspectratio": {
                "x": x_range / max_range,
                "y": y_range / max_range,
                "z": z_range / max_range,
            },
        },
        width=500,
        height=900,
        scene_camera={"eye": {"x": 1.5, "y": 0.4, "z": 0.5}},
    )

    return fig


def display_crowd2D(crowd: Crowd) -> Figure:
    """
    Display a 2D plot of a crowd of agents.

    It plots the 2D shapes of agents, with colors normalized based on their areas.

    Parameters
    ----------
    crowd : Crowd
        The crowd object containing agents with 2D geometric shapes.

    Returns
    -------
    matplotlib.figure.Figure
        A matplotlib figure object displaying the 2D plot of the crowd.

    Raises
    ------
    AttributeError
        If any agent in the crowd lacks the required 2D shape attributes.
    TypeError
        If an agent's geometric shape is neither a Polygon nor a MultiPolygon.
    """
    # Create a Normalize object to scale values between the minimum and maximum areas of 2D shapes of all agents in the crowd
    norm = Normalize(
        vmin=min(agent.shapes2D.get_area() for agent in crowd.agents),
        vmax=max(agent.shapes2D.get_area() for agent in crowd.agents),
    )

    # Initialize a Matplotlib figure
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot each agent's shape
    for agent in crowd.agents:
        agent_geometric = agent.shapes2D.get_geometric_shape()
        agent_area = agent.shapes2D.get_area()
        color = cram.cm.hawaii(norm(agent_area))  # pylint: disable=no-member

        # Check if agent_geomtetric is of type Polygon
        if isinstance(agent_geometric, Polygon):
            x, y = agent_geometric.exterior.xy
            ax.fill(x, y, alpha=0.8, color=color)
            ax.plot(x, y, color="black", linewidth=0.5)

        # If the agent's shape is a MultiPolygon, plot each polygon separately
        elif isinstance(agent_geometric, MultiPolygon):
            agent_area = agent.shapes2D.get_area()
            for polygon in agent_geometric.geoms:
                x, y = polygon.exterior.xy
                ax.fill(x, y, alpha=0.8, color=color)
                ax.plot(x, y, color="black", linewidth=0.5)

    # Determine the x and y limits based on the agents' shapes
    x_agent_min = np.min([agent.shapes2D.get_geometric_shape().bounds[0] for agent in crowd.agents])
    x_agent_max = np.max([agent.shapes2D.get_geometric_shape().bounds[2] for agent in crowd.agents])
    y_agent_min = np.min([agent.shapes2D.get_geometric_shape().bounds[1] for agent in crowd.agents])
    y_agent_max = np.max([agent.shapes2D.get_geometric_shape().bounds[3] for agent in crowd.agents])

    # Set plot properties
    ax.set_xlim(x_agent_min, x_agent_max)
    ax.set_ylim(y_agent_min, y_agent_max)
    ax.set_aspect("equal", "box")
    plt.xlabel("x [cm]")
    plt.ylabel("y [cm]")
    fig.tight_layout()

    return fig


def display_distribution(df: pd.DataFrame, column: str) -> go.Figure:
    """
    Display the distribution of a specified column in a DataFrame, separated by sex.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data. Must include a 'sex' column for grouping.
    column : str
        The name of the column for which the distribution is to be displayed.

    Returns
    -------
    plotly.graph_objs._figure.Figure
        A Plotly Figure object displaying the histograms.

    Raises
    ------
    ValueError
        If the specified column is not found in the DataFrame.
        If the 'sex' column is not found in the DataFrame.
    """
    # Check if the specified column is present in the DataFrame
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in the DataFrame.")
    if "sex" not in df.columns:
        raise ValueError("Column 'sex' not found in the DataFrame, required for hue.")

    # Initialize a Plotly figure
    fig = go.Figure()

    # Select values associated with the sex male or female
    values_male = df[df["sex"] == "male"][column]
    values_female = df[df["sex"] == "female"][column]

    # Add histograms
    fig.add_trace(
        go.Histogram(
            x=values_male,
            name="male",
            marker_color="blue",
        )
    )
    # Overlay the histograms
    fig.add_trace(
        go.Histogram(
            x=values_female,
            name="female",
            marker_color="red",
        )
    )

    # Set opacity for overlapping histograms
    fig.update_traces(opacity=0.5)

    # Add custom hover text using hovertemplate
    if column not in ["sex", "weight [kg]"]:
        fig.update_traces(hovertemplate=f"<b>{column[:-5]}</b>" + " = %{x} cm<br><b>Count = </b>%{y}</b>")
    elif column == "weight [kg]":
        fig.update_traces(hovertemplate=f"<b>{column[:-5]}</b>" + " = %{x} kg<br><b>Count = </b>%{y}</b>")
    elif column == "sex":
        fig.update_traces(hovertemplate=f"<b>{column}</b>" + " = %{x}<br><b>Count = </b>%{y}</b><extra></extra>")

    # Set layout properties
    fig.update_layout(
        barmode="overlay",
        xaxis_title=column,
        yaxis_title="Count",
        legend_title_text="",
        width=600,
        height=500,
    )

    return fig
