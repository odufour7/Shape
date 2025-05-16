"""Run the CrowdMechanics library for tests."""

import ctypes
import sys
import time
from pathlib import Path
from typing import cast

import kivy
import numpy as np
import shapely.affinity as affin
from kivy.app import App
from kivy.config import Config
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.graphics import Color, Line, Mesh, Rectangle
from kivy.graphics.tesselator import Tesselator  # pylint: disable=no-name-in-module
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.geometry.base import BaseGeometry

import configuration.utils.constants as cst
import configuration.utils.functions as fun
from configuration.models.agents import Agent
from configuration.models.measures import CrowdMeasures, create_pedestrian_measures

########## PARAMETERS ##########

# Define global parameters for the window size and system size
WS_X: int = 1000  # Windows Size X in Pixels
WS_Y: int = WS_X  # Windows Size Y in Pixels
M1: int = 40  # System Size X in cell coordinates
M2: int = M1  # System Size Y in cell coordinates
dx: float = 0.5  # x-spacing of gridpoints in meters
dy: float = dx  # y-spacing of gridpoints in meters
Lx: float = M1 * dx  # Layout width in meters
Ly: float = M2 * dy  # Layout height in meters
pixel_density: float = float(WS_X) / float(Lx)  # pixel density in pixels/meter

# Define parameters for the agents
radius: float = 0.3  # pedestrian's default radius in meters
rc = np.random.rand(100, 3)  # random colors for the agents

# Position of the Torque button
torque_button_xs: int = WS_X - 55
torque_button_ys: int = WS_Y - 200
torque_button_size: int = 40

# Define key bindings for various actions
KEY_BINDINGS = {
    "a": "Spawn agent",
    "w": "Set walls",
    "s": "Save configuration",
    " ": "Next stage",
    "q": "Quit",
}

# Create folders for static and dynamic files
folderStatic = Path().absolute() / "static"
folderDynamic = Path().absolute() / "dynamic"
Path(folderStatic).mkdir(parents=True, exist_ok=True)
Path(folderDynamic).mkdir(parents=True, exist_ok=True)

# crowd parameters
crowd_measures = CrowdMeasures()

########## AUXILIARY FUNCTIONS ##########


def get_closest_node(x: int, y: int) -> tuple[int, int]:
    """
    Get the closest grid node to a given point.

    Parameters
    ----------
    x : float
        The x-coordinate of the point.
    y : float
        The y-coordinate of the point.

    Returns
    -------
    Tuple[int, int]
        The coordinates of the closest grid node.
    """
    return (int(round(x / pixel_density / dx) * dx * pixel_density), int(round(y / pixel_density / dy) * dy * pixel_density))


def shapely_to_kivy_contours(geometry: BaseGeometry) -> list[list[float]]:
    """
    Convert a Shapely geometry (Polygon or MultiPolygon) to Kivy-compatible contours.

    Parameters
    ----------
    geometry : shapely.geometry.base.BaseGeometry
        A Shapely geometry object, either a Polygon or MultiPolygon.

    Returns
    -------
    list[list[float]]
        A list of contours, where each contour is a flat list of x, y coordinates
        suitable for Kivy tesselation.

    Notes
    -----
    - For a Polygon, the exterior and all interiors (holes) are converted to contours.
    - For a MultiPolygon, all constituent polygons are processed recursively.
    """
    contours: list[list[float]] = []
    if isinstance(geometry, Polygon):
        contours.append([coord for xy in geometry.exterior.coords for coord in xy])
        for interior in geometry.interiors:
            contours.append([coord for xy in interior.coords for coord in xy])
    elif isinstance(geometry, MultiPolygon):
        for poly in geometry.geoms:
            contours.extend(shapely_to_kivy_contours(poly))
    return contours


########## KIVY INTERFACE CLASSES ##########


class AgentKivy:
    """
    Class representing an agent in the simulation.

    Parameters
    ----------
    x : float
        The initial x-coordinate of the agent.
    y : float
        The initial y-coordinate of the agent.
    """

    def __init__(self, x: float, y: float) -> None:
        """
        Initialize an agent with position and default physical attributes.

        Parameters
        ----------
        x : float
            The initial x-coordinate of the agent.
        y : float
            The initial y-coordinate of the agent.

        Attributes
        ----------
        x : float
            The x-coordinate of the agent.
        y : float
            The y-coordinate of the agent.
        Fx : float
            The force applied in the x-direction (default: 0.0).
        Fy : float
            The force applied in the y-direction (default: 1.0).
        theta : float
            The orientation angle of the agent in radians (default: 0.0).
        torque : float
            The torque applied to the agent (default: 0.0).

        Raises
        ------
        TypeError
            If `x` or `y` is not an float.
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("x and y must be int or float")

        drawn_agent_data = np.random.choice(np.array(list(crowd_measures.default_database.values()), dtype="object"))
        agent_measures = create_pedestrian_measures(drawn_agent_data)
        current_agent_big = Agent(agent_type=cst.AgentTypes.pedestrian, measures=agent_measures)
        self.current_agent_big = current_agent_big
        agent_position: Point = self.current_agent_big.get_position()
        self.current_agent_big.translate(x * cst.M_TO_CM - agent_position.x, y * cst.M_TO_CM - agent_position.y)
        self.current_agent_big.translate_body3D(x * cst.M_TO_CM - agent_position.x, y * cst.M_TO_CM - agent_position.y, 0.0)
        agent_position_translated: Point = self.current_agent_big.get_position()
        self.x: float = agent_position_translated.x * cst.CM_TO_M
        self.y: float = agent_position_translated.y * cst.CM_TO_M
        self.Fx: float = 0.0
        self.Fy: float = 1.0
        self.theta: float = 0.0
        self.torque: float = 0.0

        current_orientation = self.current_agent_big.get_agent_orientation()
        self.current_agent_big.rotate(np.rad2deg(self.theta) - current_orientation)
        self.current_agent_big.rotate_body3D(np.rad2deg(self.theta) - current_orientation)

    def set_target(self, Fx: float, Fy: float) -> None:
        """
        Set the target force components attribute of `Agent`.

        Parameters
        ----------
        Fx : float
            The target force in the x-direction.
        Fy : float
            The target force in the y-direction.
        """
        self.Fx = Fx
        self.Fy = Fy

    def update_theta(self, theta: float) -> None:
        """
        Increment the attribute `theta` of an `Agent` by a given amount `theta`.

        Parameters
        ----------
        theta : float
            The value to add to the attribute `theta`.
        """
        self.theta += theta
        self.current_agent_big.rotate(np.rad2deg(theta - self.theta))
        self.current_agent_big.rotate_body3D(np.rad2deg(theta - self.theta))

    def update_torque(self, torque: float) -> None:
        """
        Increment the attribute `torque` of an `Agent` by a given amount `torque`.

        Parameters
        ----------
        torque : float
            The value to add to the attribute `torque`.
        """
        self.torque += torque


class Scenario:
    """Class representing the simulation scenario."""

    def __init__(self) -> None:
        """
        Initialize a Scenario instance with empty walls and agents.

        Attributes
        ----------
        walls : list[tuple[float,float]]
            A list of walls, where each wall is a list of (x, y) tuples representing wall points.
        totalwalls : int
            The total number of walls in the scenario.
        current_wallId : int
            The index of the currently active wall (for editing or drawing).
        agents : list
            A list of agents present in the scenario.
        current_agent_kivy_selected_id : int
            The index of the currently selected agent, or -1 if none is selected.
        """
        # Walls Variables
        self.walls: list[list[tuple[float, float]]] = []
        self.totalwalls: int = 0
        self.current_wallId: int = 0

        # List of agents
        self.agents: list[AgentKivy] = []
        self.current_agent_kivy_selected_id: int = -1  # index of the current agent

    def add_agent(self, x: int, y: int) -> None:
        """
        Add a new agent at the specified pixel coordinates.

        The agent's position is converted from pixel coordinates to world coordinates
        using the `pixel_density` factor, and the agent is appended to the `self.agents` list.
        The index of the newly added agent is stored in `self.current_agent_kivy_selected_id`.

        Parameters
        ----------
        x : int
            The x-coordinate of the agent in pixels.
        y : int
            The y-coordinate of the agent in pixels.
        """
        self.agents.append(AgentKivy(float(x) / pixel_density, float(y) / pixel_density))
        self.current_agent_kivy_selected_id = len(self.agents) - 1

    def add_NewWall(self, x0: int, y0: int) -> None:
        """
        Start a new wall at the specified pixel coordinates.

        Initializes a new wall by appending an empty list to `self.walls`, increments
        the total wall count, and adds the starting point (converted from pixel to world
        coordinates using `pixel_density`) to the new wall.

        Parameters
        ----------
        x0 : int
            The x-coordinate of the wall's starting point in pixels.
        y0 : int
            The y-coordinate of the wall's starting point in pixels.
        """
        self.walls.append([])
        self.totalwalls += 1
        self.walls[self.totalwalls - 1].append((float(x0) / pixel_density, float(y0) / pixel_density))

    def add_NewWallSec(self, x0: int, y0: int) -> None:
        """
        Add a new point (section) to the current wall at the specified pixel coordinates.

        Converts the given pixel coordinates to world coordinates using `pixel_density`
        and appends the point to the most recently created wall in `self.walls`.

        Parameters
        ----------
        x0 : int
            The x-coordinate of the new wall point in pixels.
        y0 : int
            The y-coordinate of the new wall point in pixels.
        """
        self.walls[self.totalwalls - 1].append((float(x0) / pixel_density, float(y0) / pixel_density))

    def get_last_WallPoint(self) -> tuple[float, float]:
        """
        Retrieve the last point added to the current wall.

        Returns
        -------
        tuple[float, float]
            The (x, y) coordinates of the last point added to the current wall.
        """
        return self.walls[self.totalwalls - 1][-1]

    def nextwall(self) -> None:
        """Start a new empty wall and increments the wall counter `self.totalwalls`."""
        self.walls.append([])
        self.totalwalls += 1

    def save(self) -> None:
        """
        Save the current geometry and agent data to XML files.

        Specifically, it creates:
            - `Geometry.xml` containing wall and geometry information, within the `static` directory.
            - `Agents.xml` containing agent properties,  within the `static` directory.
            - `AgentDynamics.xml` containing agent dynamic states,  within the `dynamic` directory.
        """
        # Walls
        with open(folderStatic / "Geometry.xml", "w", encoding="utf-8") as f:
            f.write(r'<?xml version="1.0" encoding="utf-8"?>' + "\n")
            f.write("<Geometry>\n")
            f.write(f'\t<Dimensions Lx="{Lx:.2f}" Ly="{Ly:.2f}"/>\n')
            for n, wall in enumerate(self.walls):
                f.write(f'\t<Wall Id="{n}" MaterialId="concrete">\n')
                for pt in wall:
                    f.write(f'\t\t<Corner Coordinates="{pt[0]:.2f},{pt[1]:.2f}"/>\n')
                f.write("\t</Wall>\n")
            f.write("</Geometry>")

        # Agents
        with open(folderStatic / "Agents.xml", "w", encoding="utf-8") as agentsFile:
            with open(folderDynamic / "AgentDynamics.xml", "w", encoding="utf-8") as dynamicsFile:
                agentsFile.write(r'<?xml version="1.0" encoding="utf-8"?>' + "\n")
                dynamicsFile.write(r'<?xml version="1.0" encoding="utf-8"?>' + "\n")
                agentsFile.write("<Agents>\n")
                dynamicsFile.write("<Agents>\n")
                for a, agent_kivy in enumerate(self.agents):
                    mass = agent_kivy.current_agent_big.measures.measures[cst.CommonMeasures.weight.name]
                    moment_of_inertia = agent_kivy.current_agent_big.measures.measures[cst.CommonMeasures.moment_of_inertia.name]
                    agentsFile.write(
                        f'\t<Agent Type="{agent_kivy.current_agent_big.agent_type.name}" Id="{a}" Mass="{mass:.2f}" '
                        f'fMomentOfInertia="{moment_of_inertia:.2f}" FloorDamping="2.0" '
                        'AngularDamping="5.0">\n'
                    )
                    all_shape_params = agent_kivy.current_agent_big.shapes2D.get_additional_parameters()
                    delta_g_to_gi: dict[str, tuple[float, float]] = agent_kivy.current_agent_big.get_delta_GtoGi()
                    theta: float = agent_kivy.current_agent_big.get_agent_orientation()
                    delta_g_to_gi_rotated = fun.rotate_vectors(delta_g_to_gi, -theta)
                    for shape_name, shape_params in all_shape_params.items():
                        delta_g_to_gi_shape = delta_g_to_gi_rotated[shape_name]
                        agentsFile.write(
                            f'\t\t<Shape Type="{shape_params["type"]}" Radius="{float(np.round(shape_params["radius"], 3))}" '
                            f'MaterialId="{shape_params["material"]}" '
                            f'Position="{float(np.round(delta_g_to_gi_shape[0] * cst.CM_TO_M, 3))},'
                            f'{float(np.round(delta_g_to_gi_shape[1] * cst.CM_TO_M, 3))}"/>\n'
                        )

                    dynamicsFile.write(f'\t<Agent Id="{a}">\n')
                    # Write shapes too
                    dynamicsFile.write(
                        f'\t\t<Kinematics Position="{agent_kivy.x:.2f},{agent_kivy.y:.2f}" Velocity="0,0"'
                        f' Theta="{agent_kivy.theta:.2f}" Omega="0"/>\n'
                    )
                    dynamicsFile.write(f'\t\t<Dynamics Fp="{agent_kivy.Fx:.2f},{agent_kivy.Fy:.2f}" Mp="{agent_kivy.torque:.2f}"/>\n')
                    agentsFile.write("\t</Agent>\n")
                    dynamicsFile.write("\t</Agent>\n")
                dynamicsFile.write("</Agents>")
            agentsFile.write("</Agents>")


class MyWidget(Widget):  # type: ignore[misc]
    """
    Class representing the main widget for the Kivy application.

    This class handles the drawing of the simulation environment, including walls,
    agents, and UI elements. It also manages user interactions such as mouse clicks
    and keyboard events.
    """

    def __init__(self) -> None:
        """
        Initialize the MyWidget instance with default state variables.

        Attributes
        ----------
        conf_save : bool | None
            Indicates whether the configuration has been saved.
        scenario : Scenario | None
            Reference to the current Scenario instance.
        pos_pressed : tuple[float,float] | None
            The (x, y) position of the last mouse or touch press.
        time_pressed : float | None
            The timestamp of the last mouse or touch press.
        current : int | None
            The current interaction mode or stage (e.g., wall creation, agent creation).
        drawing_walls : bool | None
            Indicates whether the user is currently drawing walls.
        """
        super().__init__()
        self.conf_save: bool | None = None
        self.scenario: Scenario | None = None
        self.pos_pressed: tuple[float, float] | None = None
        self.time_pressed: float | None = None
        self.current: int | None = None
        self.drawing_walls: bool | None = None

    def draw_cross(self, x: int, y: int, size: int) -> None:
        """
        Draw a cross centered at the specified pixel coordinates on the canvas.

        The cross consists of two diagonal lines intersecting at (x, y), each with a length determined by `size`.
        The lines are drawn using the `canvas` attribute, and their width is set to half of `size` (rounded).

        Parameters
        ----------
        x : int
            The x-coordinate of the cross center in pixels.
        y : int
            The y-coordinate of the cross center in pixels.
        size : int
            Half the length of each diagonal line of the cross.
        """
        int_x = int(x)
        int_y = int(y)
        with self.canvas:
            Line(points=(int_x - size, int_y - size, int_x + size, int_y + size), width=int(round(size / 2)))
            Line(points=(int_x + size, int_y - size, int_x - size, int_y + size), width=int(round(size / 2)))

    def draw_horizontal_line(self, y: float, size: float) -> None:
        """
        Draw a horizontal line at the specified y-coordinate on the canvas, that spans the whole canvas.

        Parameters
        ----------
        y : int
            The y-coordinate (in pixels) where the horizontal line will be drawn.
        size : int
            The thickness of the line.
        """
        with self.canvas:
            Line(points=[WS_X, int(y), 0, int(y)], width=int(round(size / 2)))

    def draw_vertical_line(self, x: float, size: float) -> None:
        """
        Draw a vertical line at the specified x-coordinate on the canvas, that spans the whole canvas.

        Parameters
        ----------
        x : int
            The x-coordinate (in pixels) where the vertical line will be drawn.
        size : int
            The thickness of the line.
        """
        with self.canvas:
            Line(points=[int(x), WS_Y, int(x), 0], width=int(round(size / 2)))

    def draw_arrow(self, xs: float, ys: float, xf: float, yf: float) -> None:
        """
        Draw an arrow from a starting point to an ending point on the canvas.

        The arrow consists of a main line connecting the start and end points, with an arrowhead
        at the endpoint. The arrowhead is formed by two short lines perpendicular to the direction
        of the main arrow.

        Parameters
        ----------
        xs : float
            The x-coordinate of the starting point (in pixels).
        ys : float
            The y-coordinate of the starting point (in pixels).
        xf : float
            The x-coordinate of the ending point (in pixels).
        yf : float
            The y-coordinate of the ending point (in pixels).
        """
        tx = xf - xs
        ty = yf - ys
        t_norm = np.sqrt(tx**2 + ty**2)
        tx /= t_norm
        ty /= t_norm
        tx1 = -tx - ty
        ty1 = -ty + tx
        tx2 = -tx + ty
        ty2 = -ty - tx

        with self.canvas:
            Line(points=(int(xs), int(ys), int(xf), int(yf)), width=2)
            Line(points=(int(xf), int(yf), int(xf) + int(10.0 * tx1), int(yf) + int(10.0 * ty1)), width=2)
            Line(points=(int(xf), int(yf), int(xf) + int(10.0 * tx2), int(yf) + int(10.0 * ty2)), width=2)

    def draw_grid(self) -> None:
        """
        Draw a grid on the canvas.

        The grid is rendered by drawing vertical and horizontal lines at regular intervals
        across the canvas. The grid color is set to a light gray. The spacing and extent
        of the grid are determined by the variables `dx`, `dy`, `Lx`, and `Ly`.
        Each grid line is drawn with a thickness of 1 pixel (since width=2 is divided by 2 in drawing line methods defined).
        """
        with self.canvas:
            Color(0.8, 0.8, 0.8, mode="bgr")
        for x in np.arange(0, Lx, dx):
            self.draw_vertical_line(float(pixel_density * x), 2)
        for y in np.arange(0, Ly, dy):
            self.draw_horizontal_line(float(pixel_density * y), 2)

    def draw_confSave(self) -> None:
        """Display a confirmation message on the center of the canvas when the configuration is saved."""
        with self.canvas:
            if self.conf_save:
                Color(0, 0, 0, mode="bgr")
                label = CoreLabel(text="Configuration Saved!", font_size=22)
                label.refresh()
                Rectangle(pos=(WS_X / 2.0 - 125, WS_Y - 100), size=(250, 40), texture=label.texture)

                label2 = CoreLabel(text="Type q to quit", font_size=11)
                label2.refresh()
                Rectangle(pos=(WS_X / 2.0 - 63, WS_Y - 125), size=(125, 20), texture=label2.texture)

    def draw_buttons(self) -> None:
        """
        Draw dynamic UI buttons and stage instructions on the canvas.

        This method renders:
            - A stage-specific instruction banner at the top-left
            - Interactive buttons on the right side with varying colors based on `self.current`
            - A torque control button with a dedicated position and color

        The button colors and text change based on the current interaction stage.
        """
        with self.canvas:
            Color(0, 0, 0, 1, mode="bgra")
            if self.current == 0:
                label = CoreLabel(text="Stage 1: Create walls (press SPACE to move on)", font_size=30)
                label.refresh()
                Rectangle(pos=(200, WS_Y - 50), size=(450, 60), texture=label.texture)
            elif self.current == 1:
                label = CoreLabel(text="Stage 2: Spawn one agent (press SPACE to move on)", font_size=30)
                label.refresh()
                Rectangle(pos=(200, WS_Y - 50), size=(450, 60), texture=label.texture)
            elif self.current == 2:
                label = CoreLabel(text="Stage 4: Run simulation (press SPACE)", font_size=30)
                label.refresh()
                Rectangle(pos=(200, WS_Y - 50), size=(450, 60), texture=label.texture)

            col_bottons = np.ones(5) * 0.3
            col_bottons[self.current] = 1

            Color(0, 0, 0, col_bottons[0], mode="bgra")
            label = CoreLabel(text="Set walls (w)", font_size=20)
            label.refresh()
            Rectangle(pos=(WS_X - 150, WS_Y - 50), size=(100, 40), texture=label.texture)

            Color(0, 0, 1, col_bottons[1], mode="bgra")
            label = CoreLabel(text="Spawn agent (a)", font_size=20)
            label.refresh()
            Rectangle(pos=(WS_X - 150, WS_Y - 100), size=(100, 40), texture=label.texture)

            Color(0.4, 0.0, 0, col_bottons[2], mode="bgra")
            label = CoreLabel(text="Add torque", font_size=20)
            label.refresh()
            Rectangle(pos=(WS_X - 150, WS_Y - 200), size=(90, 30), texture=label.texture)
            Color(0.4, 0.0, 0, 1, mode="bgra")
            Rectangle(pos=(torque_button_xs, torque_button_ys), size=(torque_button_size, torque_button_size))

    def draw_agents(self) -> None:
        """
        Render all agents on the canvas with visual indicators.

        For each agent, this method draws:
            - A circle representing the agent's position
            - Two smaller circles indicating orientation (forward/backward)
            - An arrow showing the force vector applied to the agent

        The current agent (defined by `self.scenario.current_agent_kivy_id`) is drawn with full opacity,
        while others are rendered at 30% opacity.

        Raises
        ------
        ValueError
            If `self.scenario` is not initialized.
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")

        with self.canvas:
            for cpt_agent, current_agent_kivy in enumerate(self.scenario.agents):
                geometric_agent = current_agent_kivy.current_agent_big.shapes2D.get_geometric_shape()
                agent_position: Point = current_agent_kivy.current_agent_big.get_position()
                geometric_agent_in_pixels = affin.scale(
                    geometric_agent, cst.CM_TO_M * pixel_density, cst.CM_TO_M * pixel_density, origin=agent_position
                )
                agent_position_in_pixels = affin.scale(
                    agent_position, cst.CM_TO_M * pixel_density, cst.CM_TO_M * pixel_density, origin=(0.0, 0.0)
                )
                new_agent_in_pixels = affin.translate(
                    geometric_agent_in_pixels,
                    agent_position_in_pixels.x - agent_position.x,
                    agent_position_in_pixels.y - agent_position.y,
                )
                contours = shapely_to_kivy_contours(new_agent_in_pixels)
                tess = Tesselator()
                for contour in contours:
                    tess.add_contour(contour)
                tess.tesselate()
                with self.canvas:
                    alphach = 1.0 if cpt_agent == self.scenario.current_agent_kivy_selected_id else 0.3
                    Color(rc[0, 0], rc[0, 1], rc[0, 2], alphach, mode="bgra")
                    for vertices, indices in tess.meshes:
                        Mesh(vertices=vertices, indices=indices, mode="triangle_fan")

                Color(rc[2, 0], rc[2, 1], rc[2, 2], alphach, mode="bgra")
                self.draw_arrow(
                    pixel_density * current_agent_kivy.x,
                    pixel_density * current_agent_kivy.y,
                    pixel_density * (current_agent_kivy.x + current_agent_kivy.Fx),
                    pixel_density * (current_agent_kivy.y + current_agent_kivy.Fy),
                )

    def draw_walls(self) -> None:
        """
        Draw all walls on the canvas as connected line segments.

        Raises
        ------
        ValueError
            If `self.scenario` is not initialized.
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")

        with self.canvas:
            for _, cw in enumerate(self.scenario.walls):
                Color(0, 0, 0, 1, mode="bgra")
                if len(cw) >= 2:
                    for i in range(len(cw) - 1):
                        Line(
                            points=(
                                pixel_density * cw[i][0],
                                pixel_density * cw[i][1],
                                pixel_density * cw[i + 1][0],
                                pixel_density * cw[i + 1][1],
                            ),
                            width=3,
                        )

    def redraw(self) -> None:
        """
        Redraw the entire canvas, updating all visual elements.

        This method clears the current canvas and sequentially redraws all visual components,
        including the grid, UI buttons, agents, walls, and any configuration save messages.
        """
        self.canvas.clear()
        self.draw_grid()
        self.draw_buttons()
        self.draw_agents()
        self.draw_walls()
        self.draw_confSave()

    def IsClickOnTorqueButton(self) -> bool:
        """
        Check if the last mouse click was on the torque button.

        Returns
        -------
        bool
            True if the last click was within the torque button area, False otherwise.

        Raises
        ------
        ValueError
            If `self.pos_pressed` is not initialized.

        Notes
        -----
        Returns True if the coordinates of the last pressed position (`self.pos_pressed`) are within the bounds
        of the torque button defined by the x and y coordinates of the bottom left corner and square size:

            - `torque_button_xs`
            - `torque_button_ys`
            - `torque_button_size`
        """
        if self.pos_pressed is None:
            raise ValueError("Position pressed is not initialized")

        return bool(
            torque_button_xs <= self.pos_pressed[0] < torque_button_xs + torque_button_size
            and torque_button_ys <= self.pos_pressed[1] < torque_button_ys + torque_button_size
        )

    def IsClickOnCurrentAgent(self) -> bool:
        """
        Check if the last mouse click was on the central disk of the current agent.

        Returns True if the coordinates of the last pressed position (`self.pos_pressed`) are within
        the middle disk of the current agent. The agent's disk is centered at
        (`agent.x`, `agent.y`) and has a radius of `radius`, both scaled by `pixel_density`.

        Returns
        -------
        bool
            True if the last click was within the agent's disk area, False otherwise.
        """
        if self.pos_pressed is None:
            raise ValueError("Position pressed is not initialized")
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")

        agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
        return bool(
            np.sqrt(
                (self.pos_pressed[0] - pixel_density * agent_kivy.x) ** 2 + (self.pos_pressed[1] - pixel_density * agent_kivy.y) ** 2
            )
            <= pixel_density * radius
        )

    def on_touch_up(self, touch: kivy.input.motionevent.MotionEvent) -> None:
        """
        Handle touch release events (with the mouse) for wall/agent creation and interaction.

        Parameters
        ----------
        touch : kivy.input.motionevent.MotionEvent
            The touch event object containing position and button information.

        Notes
        -----
        Behavior depends on the current interaction mode (`self.current`):
            - **Mode 0 (Wall Creation)**:
                - Right click: Stops drawing walls
                - Left click: Starts a new wall or adds points to existing walls
            - **Mode 1 (Agent Interaction)**:
                - Torque button click: Applies torque based on press duration
                - Agent click: Rotates agent based on press duration
                - Left click: Spawns new agent
                - Other clicks: Sets force target for current agent
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")
        if self.time_pressed is None:
            raise ValueError("Time pressed is not initialized")

        x, y = touch.pos

        with self.canvas:
            if self.current == 0:  # New wall
                (x1, y1) = get_closest_node(x, y)

                if touch.button == "right":
                    self.drawing_walls = False
                else:
                    if not self.drawing_walls:
                        self.scenario.add_NewWall(x1, y1)
                        self.drawing_walls = True
                    else:
                        self.scenario.add_NewWallSec(x1, y1)
                        Color(0, 0, 0, mode="bgr")
                        (x0, y0) = self.scenario.get_last_WallPoint()
                        Line(points=(x0, y0, x1, y1), width=3)

            elif self.current == 1:  # New agent
                # 1. Check if the Add torque button is being pressed
                if len(self.scenario.agents) >= 1 and self.time_pressed > 0 and self.IsClickOnTorqueButton():
                    agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
                    intensity = 0.5 * (time.time() - self.time_pressed)
                    if touch.button == "right":
                        intensity *= -1.0
                    agent_kivy.update_torque(intensity)
                    print(f"Torque={intensity:.2f}")

                # 2. Check if the Current Agent is being pressed (to rotate it)
                elif len(self.scenario.agents) >= 1 and self.time_pressed > 0 and self.IsClickOnCurrentAgent():
                    agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
                    intensity = 0.5 * (time.time() - self.time_pressed)
                    if touch.button == "right":
                        intensity *= -1.0
                    agent_kivy.update_theta(intensity)

                # 3. Spawn new agent
                elif touch.button == "left":
                    self.scenario.add_agent(x, y)
                    Color(0, 0, 1, mode="bgr")

                # 4. Set target for current agent
                elif len(self.scenario.agents) >= 1:
                    agent_kivy = self.scenario.agents[self.scenario.current_agent_kivy_selected_id]
                    F_norm = 2.0 * (time.time() - self.time_pressed) if self.time_pressed > 0 else 1.0
                    F_norm /= np.sqrt((x / pixel_density - agent_kivy.x) ** 2 + (y / pixel_density - agent_kivy.y) ** 2)
                    agent_kivy.set_target(F_norm * (x / pixel_density - agent_kivy.x), F_norm * (y / pixel_density - agent_kivy.y))

        self.time_pressed = -1
        self.canvas.clear()
        self.redraw()

    def mouse_pos(self, window: kivy.core.window.Window, touch: kivy.input.motionevent.MotionEvent) -> None:  # pylint: disable=unused-argument
        """
        Handle mouse position updates.

        This method updates the canvas periodically (every ~0.2 seconds) and draws:
            - Temporary wall segments during wall creation (mode 0)
            - Force/torque preview lines during force torque setting (mode 1)

        Parameters
        ----------
        window : kivy.core.window.Window
            The Kivy window object (unused in this implementation but required by Kivy's event system).
        touch : kivy.input.motionevent.MotionEvent
            The mouse position coordinates in pixel space. Typically contains [x, y] values.
        """
        if self.scenario is None:
            raise ValueError("Scenario is not initialized")
        if self.time_pressed is None:
            raise ValueError("Time pressed is not initialized")
        if self.pos_pressed is None:
            raise ValueError("Position pressed is not initialized")

        if not int(50 * time.time()) % 5 == 1:
            return

        self.redraw()
        with self.canvas:
            if self.current == 0:
                if self.drawing_walls:
                    Color(0, 0, 0, mode="bgr")
                    Lwp = self.scenario.get_last_WallPoint()
                    Line(points=(Lwp[0] * pixel_density, Lwp[1] * pixel_density, touch[0], touch[1]), width=3)

            elif self.time_pressed > 0:
                Color(rc[1, 0], rc[1, 1], rc[1, 2], mode="bgr")
                Line(points=(self.pos_pressed[0], self.pos_pressed[1], touch[0], touch[1]), width=3)

    def on_touch_down(self, touch: kivy.input.motionevent.MotionEvent) -> None:
        """
        Handle mouse press events, such as the initiation of a touch event or mouse click.

        Records the time and position of the mouse press for later use. If the right mouse button is pressed,
        it also stops the wall-drawing mode.

        Parameters
        ----------
         touch : kivy.input.motionevent.MotionEvent
             The touch event object containing position (`x`, `y`) and button information.
        """
        self.time_pressed = time.time()
        self.pos_pressed = (touch.x, touch.y)
        if touch.button == "right":
            self.drawing_walls = False

    def initialise(self) -> None:
        """
        Initialize the simulation environment and UI state.

        Notes
        -----
        - Sets `self.current` to 0 (wall creation mode).
        - Creates a new `Scenario` instance and assigns it to `self.scenario`.
        - Resets `self.pos_pressed` and `self.time_pressed` to invalid values.
        - Draws the initial grid and UI buttons.
        """
        self.current = 0  # 0: wall 1: agent 2: Simulate!
        self.scenario = Scenario()
        self.pos_pressed = (-1, -1)
        self.time_pressed = -1
        self.drawing_walls = False
        self.conf_save = False
        Window.bind(mouse_pos=self.mouse_pos)
        self.draw_grid()
        self.draw_buttons()


class MyApp(App):  # type: ignore[misc]
    """
    Main application class for the Kivy simulation interface.

    Attributes
    ----------
    widget : Widget | None
        Reference to the main application widget. Initialized as None and set during the build process.
    """

    def __init__(self) -> None:
        """
        Initialize the MyApp application instance.

        Attributes
        ----------
        widget : Widget | None
            Reference to the main application widget. Initialized as None and set during the build process.
        """
        super().__init__()
        self.widget: Widget | None = None

    def get_number_from_popup(self) -> None:
        """Display a popup dialog to prompt the user for input."""
        textinput = TextInput(multiline=False)
        popup = Popup(title="Enter ellipse orientation in degrees", content=textinput, size_hint=(None, None), size=(400, 200))

        def on_text_enter(instance: TextInput) -> None:
            """
            Handle the Enter key press event on the text input.

            Parameters
            ----------
            instance : TextInput
                The text input widget instance.
            """
            if not isinstance(self.widget, MyWidget):
                raise ValueError("Widget is not initialized")
            if not isinstance(self.widget.scenario, Scenario):
                raise ValueError("Scenario is not initialized")
            if self.widget.scenario is None:
                raise ValueError("Scenario is not initialized")
            try:  # it wait until the user enter a number, then the popup is dismissed (closed)
                popup.dismiss()
            except ValueError:
                instance.text = ""
                instance.hint_text = "Please enter a valid number"
            popup.dismiss()

        textinput.bind(on_text_validate=on_text_enter)  # pylint: disable=no-member
        popup.open()

    def key_action(self, keyboard: object, keycode0: int, keycode1: int, text: str, modifiers: list[str]) -> None:  # pylint: disable=unused-argument
        """
        Handle keyboard input events for controlling the application workflow.

        Parameters
        ----------
        keyboard : object
            Kivy keyboard reference (unused but required by Kivy event system).
        keycode0 : int
            Native keycode (unused but required by Kivy event system).
        keycode1 : int
            Kivy keycode (unused but required by Kivy event system).
        text : str
            The character representation of the pressed key.
        modifiers : list
            Active modifier keys (e.g., shift, ctrl) - unused but required by Kivy event system.

        Notes
        -----
        Here are the key bindings:
            - 'a' : Switch to agent creation mode
            - 'w' : Switch to wall creation mode
            - 's' : Save current configuration
            - ' ' : Space - Advance to next interaction stage
            - 'q' : Quit the application

        The stage progression (space bar) cycles through modes: walls -> agents -> simulation
        """
        if self.widget is None:
            raise ValueError("Widget is not initialized")

        if text == "a":  # Spawn agent
            self.widget.current = 1
            self.widget.drawing_walls = False
            self.widget.redraw()

        elif text == "w":  # Set walls
            self.widget.current = 0
            self.widget.drawing_walls = False
            self.widget.scenario.current_wallId = 0
            self.widget.redraw()

        elif text == "s":  # Save configuration
            self.widget.conf_save = True
            self.widget.draw_confSave()
            self.widget.scenario.save()

        elif text == " ":  # Space bar, move to next stage
            self.widget.conf_save = True
            if self.widget.current < 3:
                self.widget.current += 1
                self.widget.draw_confSave()
                self.widget.scenario.save()
            else:
                pass  #!! RUN ONE STEP OF THE MECHANICAL LAYER

        elif text == "q":  # Quit
            sys.exit()

    def build(self) -> Widget:
        """
        Build and initialize the main application widget.

        Returns
        -------
        Widget
            The main application widget (`self.widget`) that serves as the root of the UI.

        Notes
        -----
        - Sets the window background color to white `(1, 1, 1, 1)` (opaque white).
        - Sets the window size using the global constants `WS_X` and `WS_Y`.
        - Binds the `on_key_down` event of the window to `self.key_action` for keyboard input handling.
        """
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (WS_X, WS_Y)
        self.widget = MyWidget()
        self.widget.initialise()

        Window.bind(on_key_down=self.key_action)
        return self.widget


if __name__ == "__main__":
    # Set Kivy configuration to use the mouse
    Config.set("input", "mouse", "mouse,multitouch_on_demand")

    # Load the CrowdMechanics library into ctypes
    libname = str(Path().absolute().parent.parent / "src" / "mechanical_layer" / "build" / "libCrowdMechanics.dylib")
    mechanicalLayer = ctypes.CDLL(libname)
    files = [
        b"/Volumes/desk_oscar/main/cours/phd_first_year/shape_project/code/tests/mechanical_layer/Parameters.xml",
        b"Materials.xml",
        b"Geometry.xml",
        b"Agents.xml",
        b"AgentDynamics.xml",
    ]
    nFiles = len(files)
    filesInput = cast(list[ctypes.c_char_p | bytes | None], (ctypes.c_char_p * nFiles)())
    filesInput[:] = files

    MyApp().run()
