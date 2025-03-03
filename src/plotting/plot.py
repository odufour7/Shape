""" This module contains functions to plot the geometric shapes of the pedestrian and the crowd. """

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pyvista as pv
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable
from streamlit.delta_generator import DeltaGenerator

import src.utils.functions as fun
from src.classes.agents import Agent
from src.classes.trial.crowd_old import Crowd

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
    """Draws the 2D shape of the pedestrian using Plotly."""

    fig = go.Figure()
    for id_agent, agent in enumerate(agents):
        id_agent += 1
        geometric_agent = agent.shapes2D.get_geometric_shape()
        agent_type = agent.agent_type
        if geometric_agent.geom_type == "Polygon":
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
        elif geometric_agent.geom_type == "MultiPolygon":
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


def display_body3D_orthogonal_projection(agent: Agent, extra_info: list[DeltaGenerator, str]) -> None:
    """Draws the orthogonal projection of the pedestrian's body."""

    fig, ax = plt.subplots(figsize=(11, 11))
    sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(vmin=0, vmax=max(agent.shapes3D.shapes.keys())))

    # Plot each polygon with its corresponding height-based color
    min_height = min(agent.shapes3D.shapes.keys())
    max_height = max(agent.shapes3D.shapes.keys())
    for height, multi_polygon in sorted(agent.shapes3D.shapes.items()):
        percent_completed = (height - min_height) / (max_height - min_height)
        fun.update_progress_bar(extra_info[0], extra_info[1], percent_completed)
        for polygon in multi_polygon.geoms:
            x, y = polygon.exterior.xy
            ax.plot(x, y, color=sm.to_rgba(height), alpha=0.6, linewidth=2)

    # Create a divider and append axes for the colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.2)

    # Add a colorbar with inverted orientation (red at top)
    cbar = plt.colorbar(sm, cax=cax)
    cbar.set_label("Height [cm]")

    # Set plot title and labels
    ax.set_title(f"Orthogonal projection of a {agent.measures.measures["sex"]}")
    ax.margins(0)
    ax.set_aspect("equal")
    ax.set_xlabel("X [cm]")
    ax.set_ylabel("Y [cm]")
    plt.tight_layout()

    return fig


def display_body3D_polygons(agent: Agent, extra_info: list[DeltaGenerator, str]) -> go.Figure:
    """Draws the 3D body of the pedestrian."""

    # Initialize a Plotly figure
    fig = go.Figure()

    # Normalize heights for color mapping
    max_height = max(agent.shapes3D.shapes.keys())
    min_height = min(agent.shapes3D.shapes.keys())

    # Add each polygon to the 3D plot
    for height, multi_polygon in sorted(agent.shapes3D.shapes.items(), reverse=True):
        # Reverse order for proper layering (start from top)

        normalized_height = (height - min_height) / (max_height - min_height)  # Normalize height for color scale

        percent_completed = (max_height - height - min_height) / (max_height - min_height)
        fun.update_progress_bar(extra_info[0], extra_info[1], percent_completed)

        # Assign color based on normalized height
        if agent.measures.measures["sex"] == "female":
            # Gradient from red to yellow
            color = f"rgba(255, {int(205 * (normalized_height))}, {int(205 * (1-normalized_height))}, 0.8)"
        else:
            # Gradient from red to blue
            color = f"rgba({int(205 * (1-normalized_height))}, {int(205 * (normalized_height))}, 255, 0.8)"

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

    # Determine axis ranges to set equal scale
    x_range = np.ptp(
        [x for multi_polygon in agent.shapes3D.shapes.values() for polygon in multi_polygon.geoms for x in polygon.exterior.xy[0]]
    )
    y_range = np.ptp(
        [y for multi_polygon in agent.shapes3D.shapes.values() for polygon in multi_polygon.geoms for y in polygon.exterior.xy[1]]
    )
    z_range = max_height - min_height
    max_range = max(x_range, y_range, z_range)

    # Customize the layout with same scale for all axes and add colorbar
    fig.update_layout(
        # title=f"3D body representation of a {ped.sex}<br>   as a superposition of slices",
        scene={
            "xaxis_title": "X [cm]",
            "yaxis_title": "Y [cm]",
            "zaxis_title": "Height [cm]",
            "aspectmode": "manual",  # Use manual mode to set aspect ratio explicitly
            "aspectratio": {
                "x": x_range / max_range,
                "y": y_range / max_range,
                "z": z_range / max_range,
            },
            # change with and height of the plot
        },
        showlegend=False,
        width=500,
        height=900,
        scene_camera={"eye": {"x": 1.5, "y": 0.4, "z": 0.5}},
    )

    return fig


def display_body3D_mesh(agent: Agent, extra_info: list[DeltaGenerator, str, int]) -> go.Figure:
    """
    Draws a continuous 3D mesh connecting contours at different heights using Plotly's Mesh3d.
    Fills missing triangles and smooths the mesh for better visualization.
    """

    # Reduce the number of heights to process
    precision = extra_info[2]
    new_body = {
        height: multi_polygon for idx, (height, multi_polygon) in enumerate(agent.shapes3D.shapes.items()) if idx % precision == 0
    }
    print(f"Number of heights: {len(new_body)}")

    # Extract sorted heights
    sorted_heights = np.array(sorted(new_body.keys(), reverse=True))

    # Initialize lists for vertices and triangles
    all_points = np.empty((0, 3), dtype=float)
    all_triangles = np.empty((0, 3), dtype=int)

    # Iterate through pairs of consecutive heights
    for h_idx in range(len(sorted_heights) - 1):
        percent_completed = (sorted_heights[0] - sorted_heights[h_idx] - sorted_heights[-1]) / (
            sorted_heights[0] - sorted_heights[-1]
        )
        fun.update_progress_bar(extra_info[0], extra_info[1], percent_completed)

        height_high, height_low = sorted_heights[h_idx], sorted_heights[h_idx + 1]
        high_contours, low_contours = new_body[height_high], new_body[height_low]

        for polygon_high in high_contours.geoms:
            # Extract coordinates for high and low contours
            x_high, y_high = polygon_high.exterior.xy
            x_high, y_high = np.array(x_high), np.array(y_high)
            z_high = np.full_like(x_high, height_high)

            x_low, y_low = fun.extract_coordinates(low_contours)
            z_low = np.full_like(x_low, height_low)

            # Append vertices
            start_idx_high = all_points.shape[0]
            points_high = np.column_stack((x_high, y_high, z_high))
            all_points = np.vstack((all_points, points_high))

            start_idx_low = all_points.shape[0]
            points_low = np.column_stack((x_low, y_low, z_low))
            all_points = np.vstack((all_points, points_low))

            # Create triangular meshes between high and low contours
            for idx in range(len(x_high) - 1):  # Loop through consecutive points on high contour
                # Find the nearest point on the low contour
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

    # Fill holes in the mesh using PyVista
    faces = np.column_stack((np.full(len(all_triangles), 3), all_triangles)).flatten()
    mesh_pv = pv.PolyData(all_points, faces)
    try:
        filled_mesh_pv = mesh_pv.fill_holes(5.0)
        points_filled = filled_mesh_pv.points
        faces_filled = filled_mesh_pv.faces.reshape(-1, 4)[:, 1:]
        all_triangles_filled = faces_filled
    except (ValueError, RuntimeError) as e:
        print(f"Error filling holes: {e}")
        all_triangles_filled = all_triangles

    # Remove triangles associated with the last layer of vertices (if needed) with filter_mesh_by_z_threshold
    # because for the smallest height, we only have one leg and more precisely, just a few toes
    min_height = min(agent.shapes3D.shapes.keys())
    points_filled, all_triangles_filled = fun.filter_mesh_by_z_threshold(
        points_filled, all_triangles_filled, z_threshold=min_height + 0.1
    )

    # Normalize z-coordinates for color mapping
    color_scale_name = "viridis" if agent.measures.measures["sex"] == "male" else "inferno"
    norm = Normalize(vmin=np.min(points_filled[:, 2]), vmax=np.max(points_filled[:, 2]))
    colorscale_values = norm(points_filled[:, 2])
    colorscale_values = cm.get_cmap(color_scale_name)(colorscale_values)[:, :3]
    vertex_colors = [f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})" for r, g, b in colorscale_values]

    print("\nPlotting...")

    # Create a Mesh3d plot with Plotly
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

    # Set aspect ratio for equal scaling
    x_range = np.ptp(points_filled[:, 0])
    y_range = np.ptp(points_filled[:, 1])
    z_range = np.ptp(points_filled[:, 2])
    max_range = max(x_range, y_range, z_range)

    fig.update_layout(
        title=f"3D body representation of a {agent.measures.measures["sex"]} with a mesh",
        scene={
            "xaxis_title": "X [cm]",
            "yaxis_title": "Y [cm]",
            "zaxis_title": "Height [cm]",
            "aspectmode": "manual",
            "aspectratio": {"x": x_range / max_range, "y": y_range / max_range, "z": z_range / max_range},
        },
        width=500,
        height=900,
        scene_camera={"eye": {"x": 1.5, "y": 0.4, "z": 0.5}},
    )

    return fig


def display_crowd2D(crowd: Crowd) -> plt.Figure:
    """Draw the crowd of pedestrians in the room."""

    fig, ax = plt.subplots(figsize=(8, 8))
    for ped in crowd.packed_crowd.values():
        ped_geometric = ped.calculate_geometric_shape()
        x, y = ped_geometric.exterior.xy
        ax.fill(x, y, alpha=0.8)
        ax.plot(x, y, color="black", linewidth=0.5)
    x_min, y_min, x_max, y_max = crowd.boundaries.bounds
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal", "box")
    plt.xlabel("x [cm]")
    plt.ylabel("y [cm]")
    fig.tight_layout()
    return fig


def display_distribution(df: pd.DataFrame, column: str):
    """Display the distribution of a given column in a DataFrame using Plotly."""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in the DataFrame.")
    if "Sex" not in df.columns:
        raise ValueError("Column 'Sex' not found in the DataFrame, required for hue.")
    fig = go.Figure()

    values_male = df[df["Sex"] == "male"][column]
    values_female = df[df["Sex"] == "female"][column]

    fig.add_trace(
        go.Histogram(
            x=values_male,
            name="male",
            marker_color="blue",
        )
    )
    fig.add_trace(
        go.Histogram(
            x=values_female,
            name="female",
            marker_color="red",
        )
    )
    fig.update_layout(barmode="overlay")
    fig.update_traces(opacity=0.5)
    # Add custom hover text using hovertemplate
    if column != "Sex":
        fig.update_traces(hovertemplate=f"<b>{column[:-5]}</b>" + " = %{x} cm<br><b>Count = </b>%{y}</b>")
    else:
        fig.update_traces(hovertemplate=f"<b>{column}</b>" + " = %{x}<br><b>Count = </b>%{y}</b><extra></extra>")

    fig.update_layout(xaxis_title=column, yaxis_title="Count", legend_title_text="", width=600, height=500)

    return fig
