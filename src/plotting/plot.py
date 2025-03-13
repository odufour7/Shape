"""Contains functions to plot the geometric shapes of the pedestrian and the crowd."""

import logging

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

import src.utils.functions as fun
from src.classes.agents import Agent
from src.classes.crowd import Crowd

plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "font.size": 23,
        "text.latex.preamble": r"\usepackage{amsmath}",
    }
)


def display_shape2D(agents: list[Agent]) -> go.Figure:
    """Draw 2D geometric shapes of either pedestrian or bike using Plotly.

    This function plots the 2D shapes of agents on a Plotly figure. It supports both Polygon and MultiPolygon geometries.
    Each shape is filled with semi-transparent red color, outlined in black, and annotated with the agent's ID at its centroid.
    The figure layout is configured with equal axis scaling, no grid lines, and predefined margins.

    Parameters
    ----------
    agents : list[Agent]
        A list of Agent objects, each containing a 2D geometric shape.

    Returns
    -------
    go.Figure
        A Plotly Figure object displaying the 2D shapes of the agents.

    """
    # Initialize a Plotly figure
    fig = go.Figure()

    # Add each agent's shape to the plot
    for id_agent, agent in enumerate(agents):
        id_agent += 1
        geometric_agent = agent.shapes2D.get_geometric_shape()
        if isinstance(geometric_agent.geom_type, Polygon):
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
        elif isinstance(geometric_agent.geom_type, MultiPolygon):
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
    """Draws the orthogonal projection of the pedestrian's body.

    Parameters
    ----------
    agent : Agent
        The agent object containing the 3D shapes and measures of the pedestrian.
    extra_info : list[DeltaGenerator, str]
        A list containing a DeltaGenerator object for updating the progress bar and a string for additional information.

    Returns
    -------
        None

    """
    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    # Create a ScalarMappable object for color mapping
    sm = plt.cm.ScalarMappable(
        cmap="coolwarm",
        norm=Normalize(vmin=0, vmax=float(max(agent.shapes3D.shapes.keys()))),
    )

    # Initialize a Matplotlib figure
    fig, ax = plt.subplots(figsize=(11, 11))

    # Normalize heights for color mapping
    min_height = float(min(agent.shapes3D.shapes.keys()))
    max_height = float(max(agent.shapes3D.shapes.keys()))

    # Plot each polygon at different heights
    for height_str, multi_polygon in sorted(agent.shapes3D.shapes.items()):
        if not isinstance(multi_polygon, MultiPolygon):
            raise ValueError("multi_polygon is not a MultiPolygon")
        height = float(height_str)
        percent_completed = (height - min_height) / (max_height - min_height)
        fun.update_progress_bar(extra_info[0], extra_info[1], percent_completed)
        for polygon in multi_polygon.geoms:
            x, y = polygon.exterior.xy
            ax.plot(x, y, color=sm.to_rgba(np.array([height])), alpha=0.6, linewidth=2)

    # Add a colorbar with inverted orientation (red at top)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.2)

    # Set colorbar properties
    cbar = plt.colorbar(sm, cax=cax)
    cbar.set_label("Height [cm]")

    # Set plot properties
    ax.set_title(f"Orthogonal projection of a {agent.measures.measures['sex']}")
    ax.margins(0)
    ax.set_aspect("equal")
    ax.set_xlabel("X [cm]")
    ax.set_ylabel("Y [cm]")
    plt.tight_layout()

    return fig


def compute_range(agent: Agent, axis: str) -> float:
    """Compute the range (ptp) of coordinates along a given axis ('x' or 'y')."""
    if axis not in ("x", "y"):
        raise ValueError("Axis must be 'x' or 'y'")

    coord_index = 0 if axis == "x" else 1  # Determine index for x or y coordinates
    coordinates: list[float] = []
    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    for multi_polygon in agent.shapes3D.shapes.values():
        if not isinstance(multi_polygon, MultiPolygon):
            raise ValueError("multi_polygon is not a MultiPolygon")

        # Extract coordinates for the given axis from all polygons
        coordinates.extend(coord[coord_index] for polygon in multi_polygon.geoms for coord in polygon.exterior.xy)

    xy_range: float = np.ptp(coordinates)  # Compute and return the range
    return xy_range


def display_body3D_polygons(agent: Agent, extra_info: tuple[DeltaGenerator, DeltaGenerator]) -> go.Figure:
    """Display a 3D visualization of body polygons using Plotly.

    This function visualizes an agent's 3D body representation by plotting polygons at different heights.
    Polygons are color-coded according to the agent's height and sex.

    Parameters
    ----------
    agent : Agent
        The agent object containing 3D shapes and associated measurements.
    extra_info : list[DeltaGenerator, str]
        A list containing a progress bar object and a status message string used for updating progress.

    Returns
    -------
    go.Figure
        A Plotly figure object representing the 3D body polygons.

    """
    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    # Initialize a Plotly figure
    fig = go.Figure()

    # Normalize heights for color mapping
    max_height = float(max(agent.shapes3D.shapes.keys()))
    min_height = float(min(agent.shapes3D.shapes.keys()))

    # Add each polygon to the 3D plot
    for height_str, multi_polygon in sorted(agent.shapes3D.shapes.items(), reverse=True):
        if not isinstance(multi_polygon, MultiPolygon):
            raise ValueError("multi_polygon is not a MultiPolygon")

        height = float(height_str)

        # Normalize height for color scale
        normalized_height = (height - min_height) / (max_height - min_height)  # Normalize height for color scale

        # Update progress bar
        percent_completed = (max_height - height - min_height) / (max_height - min_height)
        fun.update_progress_bar(extra_info[0], extra_info[1], percent_completed)

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
    """Draw a continuous 3D mesh connecting contours at different heights.

    This function generates a smooth 3D mesh visualization of an agent by connecting shape contours
    at various heights using Plotly's Mesh3d.
    It fills missing triangles and smooths the mesh surface for improved visualization.

    Parameters
    ----------
    agent : Agent
        An instance of the Agent class containing 3D shape data.
    extra_info : list
        A list containing:
        - DeltaGenerator: Streamlit object for updating the progress bar.
        - str: Identifier string for the progress bar.
        - int: Precision level used to reduce the number of processed heights.

    Returns
    -------
    go.Figure
        A Plotly Figure object displaying the generated 3D mesh.

    """
    # Check if the agent's 3D shapes are available
    if agent.shapes3D is None or agent.shapes3D.shapes is None:
        raise ValueError("agent.shapes3D or agent.shapes3D.shapes is None")

    # Extract every nth height to reduce the number of vertices
    precision = extra_info[2]
    new_body = {
        height: multi_polygon for idx, (height, multi_polygon) in enumerate(agent.shapes3D.shapes.items()) if idx % precision == 0
    }
    logging.info("Number of heights: %d", len(new_body))

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
    min_height = float(min(agent.shapes3D.shapes.keys()))
    points_filled, all_triangles_filled = fun.filter_mesh_by_z_threshold(
        points_filled, all_triangles_filled, z_threshold=min_height + 0.1
    )

    # Normalize the height values for color mapping
    color_scale_name = "viridis" if agent.measures.measures["sex"] == "male" else "inferno"
    norm = Normalize(vmin=np.min(points_filled[:, 2]), vmax=np.max(points_filled[:, 2]))
    colorscale_values = norm(points_filled[:, 2])
    colorscale_values = plt.cm.get_cmap(color_scale_name)(colorscale_values)[:, :3]
    vertex_colors = [f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})" for r, g, b in colorscale_values]

    logging.info("\nPlotting...")

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
    """Display a 2D plot of a crowd of agents.

    This function visualizes the 2D shapes of agents in a crowd using matplotlib. It normalizes the colors
    of the agents based on their areas and plots their shapes. Both Polygon and MultiPolygon geometries are supported.
    The plot's x and y limits are set based on the bounds of the agents' shapes, and the aspect ratio is adjusted to be equal.

    Parameters
    ----------
    crowd : Crowd
        The crowd object containing agents with 2D geometric shapes.

    Returns
    -------
    plt.Figure
        A matplotlib figure object displaying the 2D plot of the crowd.

    """
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

        if isinstance(agent_geometric.geom_type, Polygon):
            x, y = agent_geometric.exterior.xy
            ax.fill(x, y, alpha=0.8, color=color)
            ax.plot(x, y, color="black", linewidth=0.5)

        # If the agent's shape is a MultiPolygon, plot each polygon separately
        elif isinstance(agent_geometric.geom_type, MultiPolygon):
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
    """Display the distribution of a specified column in a DataFrame, separated by sex.

    This function creates overlaid histograms for the specified column, with separate distributions
    for male and female values. Each sex is represented with a distinct color for better visualization.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data.
    column : str
        The name of the column for which the distribution is to be displayed.

    Returns
    -------
    plotly.graph_objs._figure.Figure
        A Plotly Figure object displaying the histogram.

    Raises
    ------
    ValueError
        If the specified column or the 'sex' column is not found in the DataFrame.

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
    if column != "sex":
        fig.update_traces(hovertemplate=f"<b>{column[:-5]}</b>" + " = %{x} cm<br><b>Count = </b>%{y}</b>")
    else:
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
