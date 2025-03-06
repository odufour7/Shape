"""This module contains the Crowd class, which represents a crowd of pedestrians in a room."""

import numpy as np
from scipy.spatial import ConvexHull
from shapely.geometry import Point, Polygon

import src.utils.constants as cst
from src.classes.agents import Agent
from src.classes.measures import AgentMeasures, CrowdMeasures, draw_agent_part, draw_agent_type


class Crowd:
    """Class representing a crowd of pedestrians in a room."""

    def __init__(
        self,
        measures: dict[str, float] | CrowdMeasures = None,
        agents: list[Agent] = None,
        boundaries: Polygon = None,
    ):
        if isinstance(measures, dict):
            measures = CrowdMeasures(measures)
        elif measures is None:
            measures = CrowdMeasures()  # Create a default CrowdMeasures object
        elif (measures is not None) and (not isinstance(measures, CrowdMeasures)):
            raise ValueError("`measures` should be an instance of Measures or a dictionary.")

        if agents is None:
            agents = []

        if not isinstance(agents, list) or not all(isinstance(agent, Agent) for agent in agents):
            raise ValueError("'agents' should be a list of Agent instances")

        if boundaries is None:
            boundaries = Polygon(
                [
                    (-(10**6), -(10**6)),
                    (-(10**6), 10**6),
                    (10**6, 10**6),
                    (10**6, -(10**6)),
                ]
            )
        if not isinstance(boundaries, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance")

        self._measures = measures
        self._agents = agents
        self._boundaries = boundaries

    @property
    def agents(self) -> list[Agent]:
        """Get the list of agents in the crowd."""
        return self._agents

    @agents.setter
    def agents(self, value: list[Agent]) -> None:
        """Set the agents of the crowd"""
        if not isinstance(value, list) or not all(isinstance(agent, Agent) for agent in value):
            raise ValueError("'agents' should be a list of Agent instances")
        if value is None:
            value = []
        self._agents = value

    @property
    def measures(self) -> dict[str, float] | CrowdMeasures:
        """Get the measures of the crowd."""
        return self._measures

    @measures.setter
    def measures(self, value: dict[str, float] | CrowdMeasures) -> None:
        """Set the measures of the crowd"""
        if isinstance(value, dict):
            value = CrowdMeasures(value)
        elif (value is not None) and (not isinstance(value, CrowdMeasures)):
            raise ValueError("`measures` should be an instance of Measures or a dictionary.")
        if value is None:
            value = CrowdMeasures()
        self._measures = value

    @property
    def boundaries(self) -> Polygon:
        """Get the boundaries of the room."""
        return self._boundaries

    @boundaries.setter
    def boundaries(self, value: Polygon) -> None:
        """Set the boundaries of the room"""
        if not isinstance(value, Polygon):
            raise ValueError("'boundaries' should be a shapely Polygon instance")
        self._boundaries = value

    def get_number_agents(self) -> int:
        """Get the number of agents in the crowd."""
        return len(self._agents)

    def add_one_agent(self) -> None:
        """Adds an agent of the specified type to the crowd."""
        if self.measures.agent_statistics and not self.measures.custom_database:
            drawn_agent_type = draw_agent_type()
            if drawn_agent_type == cst.AgentTypes.pedestrian.name:
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.pedestrian.name,
                    measures={
                        "sex": draw_agent_part(cst.PedestrianParts.sex.name, self.measures),
                        "bideltoid_breadth": draw_agent_part(cst.PedestrianParts.bideltoid_breadth.name, self.measures),
                        "chest_depth": draw_agent_part(cst.PedestrianParts.chest_depth.name, self.measures),
                        "height": cst.DEFAULT_HEIGHT,
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent_type, measures=agent_measures))
            elif drawn_agent_type == cst.AgentTypes.bike.name:
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.bike.name,
                    measures={
                        "wheel_width": draw_agent_part(cst.BikeParts.wheel_width.name, self.measures),
                        "total_length": draw_agent_part(cst.BikeParts.total_length.name, self.measures),
                        "handlebar_length": draw_agent_part(cst.BikeParts.handlebar_length.name, self.measures),
                        "top_tube_length": draw_agent_part(cst.BikeParts.top_tube_length.name, self.measures),
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent_type, measures=agent_measures))
        elif self.measures.custom_database and not self.measures.agent_statistics:
            # Draw an agent from the custom database
            drawn_agent = np.random.choice(list(self.measures.custom_database.values()))
            if drawn_agent["agent_type"] == cst.AgentTypes.pedestrian.name:
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.pedestrian.name,
                    measures={
                        "sex": drawn_agent["sex"],
                        "bideltoid_breadth": drawn_agent["bideltoid breadth [cm]"],
                        "chest_depth": drawn_agent["chest depth [cm]"],
                        "height": drawn_agent["height [cm]"],
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent["agent_type"], measures=agent_measures))
            elif drawn_agent["agent_type"] == cst.AgentTypes.bike.name:
                agent_measures = AgentMeasures(
                    agent_type=cst.AgentTypes.bike.name,
                    measures={
                        "wheel_width": drawn_agent["wheel width [cm]"],
                        "total_length": drawn_agent["total length [cm]"],
                        "handlebar_length": drawn_agent["handlebar length [cm]"],
                        "top_tube_length": drawn_agent["top tube length [cm]"],
                    },
                )
                self.agents.append(Agent(agent_type=drawn_agent["agent_type"], measures=agent_measures))
        elif not self.measures.custom_database and not self.measures.agent_statistics:
            # draw an angent from the default ANSURII database
            drawn_agent = np.random.choice(list(self.measures.default_database.values()))
            agent_measures = AgentMeasures(
                agent_type=cst.AgentTypes.pedestrian.name,
                measures={
                    "sex": drawn_agent["sex"],
                    "bideltoid_breadth": drawn_agent["bideltoid breadth [cm]"],
                    "chest_depth": drawn_agent["chest depth [cm]"],
                    "height": drawn_agent["height [cm]"],
                },
            )
            self.agents.append(Agent(agent_type=cst.AgentTypes.pedestrian.name, measures=agent_measures))

    def remove_one_agent(self) -> None:
        """Remove one agent from the crowd."""
        if self.agents:
            self.agents.pop()  # Remove the last agent in the list

    def create_agents(self, number_agents: float) -> None:
        """Create a number of agents in the crowd."""
        for _ in range(int(number_agents)):
            self.add_one_agent()

    def get_crowd_measures(self) -> dict[str, float]:
        """Get the crowd statistics."""
        crowd_measures = {}

        # Loop over the enumeration of AgentTypes to get the number of pedestrians and bikes
        for agent_type in cst.AgentTypes:
            count = sum(1 for agent in self.agents if agent.agent_type == agent_type.name)
            crowd_measures[f"num_{agent_type.name}"] = count

        # Loop over PedestrianParts and BikeParts to get statistics for each measure
        for parts_enum in [cst.PedestrianParts, cst.BikeParts]:
            for part in parts_enum:
                measures = [agent.measures.__dict__[part.name] for agent in self.agents if hasattr(agent.measures, part.name)]
                if measures:
                    crowd_measures[f"{part.name}_mean"] = sum(measures) / len(measures)
                    crowd_measures[f"{part.name}_std_dev"] = (
                        sum((x - crowd_measures[f"{part.name}_mean"]) ** 2 for x in measures) / (len(measures) - 1)
                    ) ** 0.5
                    crowd_measures[f"{part.name}_min"] = min(measures)
                    crowd_measures[f"{part.name}_max"] = max(measures)

        return crowd_measures

    def get_agents_params(self) -> list[dict[str, float]]:
        """Get the parameters of each agent in the crowd."""
        crowd_dict = {
            f"agent{id_agent}": {
                "agent_type": agent.agent_type,
                "shapes": agent.shapes2D.get_additional_parameters(),
            }
            for id_agent, agent in enumerate(self.agents)
        }
        return crowd_dict

    def calculate_interpenetration(self, with_inflation: bool = False) -> float:
        """Calculate the interpenetration area between pedestrians"""
        interpenetration = 0.0
        n_agents = self.get_number_agents()

        for i_agent, current_agent in enumerate(self.agents):
            current_geometric = current_agent.shapes2D.get_geometric_shape()
            if with_inflation:
                current_geometric = current_geometric.buffer(5.0)
            # Contact with other agents
            for j in range(i_agent + 1, n_agents):
                neigh_agent = self.agents[j]
                neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                if with_inflation:
                    neigh_geometric = neigh_geometric.buffer(5.0)
                interpenetration += current_geometric.intersection(neigh_geometric).area
            # Contact with boundaries
            interpenetration += current_geometric.difference(self.boundaries).area

        return interpenetration

    def compute_crowd_convex_hull_area(self) -> float:
        """Compute the convex hull of the crowd."""
        points = []
        for agent in self.agents:
            points.extend(agent.shapes2D.get_geometric_shape().exterior.coords[:-1])
        hull = ConvexHull(points)
        return hull.area

    def compute_energy(self) -> float:
        """Compute the energy of the crowd."""
        interpenetration = self.calculate_interpenetration(with_inflation=True)
        convex_hull_area = self.compute_crowd_convex_hull_area()
        return 100.0 * interpenetration + convex_hull_area / 10.0

    def pack_agents_MCMC(self) -> float:
        """Run an algorithm to pack the agents of the crowd."""

        current_energy = self.compute_energy()
        cpt_rejected = 0
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Choose a random agent
            agent = np.random.choice(self.agents)
            # Perform random move
            dtheta = np.random.uniform(-cst.MAX_ROTATION, cst.MAX_ROTATION)
            dx, dy = (
                np.random.uniform(-cst.MAX_MOVE_X, cst.MAX_MOVE_X),
                np.random.uniform(-cst.MAX_MOVE_Y, cst.MAX_MOVE_Y),
            )
            agent.rotate(dtheta)
            agent.translate(dx, dy)
            # Calculate new energy
            new_energy = self.compute_energy()
            delta_energy = new_energy - current_energy
            # Accept or reject the move
            if delta_energy < 0.0:  # if the new energy is lower, accept the move
                current_energy = new_energy
            else:  # Reject the move
                cpt_rejected += 1
                agent.rotate(-dtheta)
                agent.translate(-dx, -dy)
        # print(f"Proportion of rejected move: {100 * cpt_rejected / (cst.MAX_NB_ITERATIONS * len(self.agents)):.2f} %")

        return current_energy

    @staticmethod
    def calculate_repulsive_force(agent_centroid: np.ndarray, other_centroid: np.ndarray) -> np.ndarray:
        """Calculate the repulsive force between two centroids."""
        delta = agent_centroid - other_centroid
        norm_delta = np.linalg.norm(delta)
        if norm_delta != 0:
            return delta / norm_delta
        return 20.0 * np.random.rand(2)  # Small random force if centroids coincide

    @staticmethod
    def calculate_rotational_force() -> float:
        """Calculate a rotational force based on the agent's current orientation."""
        return np.random.uniform(-10.0, 10.0)  # Random rotational force between -10 and 10 degrees

    def pack_agents_with_forces(self) -> None:
        """Simulates the application of forces on agents within a polygonal cell over a number of iterations."""
        Temperature = 1.0
        for _ in range(cst.MAX_NB_ITERATIONS):
            # Check for overlaps and apply forces if necessary
            for i_agent, current_agent in enumerate(self.agents):
                force = np.array([0.0, 0.0])
                rotational_force = 0.0
                current_geometric = current_agent.shapes2D.get_geometric_shape()
                current_centroid = np.array(current_geometric.centroid.coords[0])
                # Calculate repulsive force between agents
                for j_agent, neigh_agent in enumerate(self.agents):
                    neigh_geometric = neigh_agent.shapes2D.get_geometric_shape()
                    if i_agent != j_agent and current_geometric.intersects(neigh_geometric):
                        neigh_centroid = np.array(neigh_geometric.centroid.coords[0])
                        force += Crowd.calculate_repulsive_force(current_centroid, neigh_centroid)
                        # compute l'aire d'intersection of the two agents
                        rotational_force += Crowd.calculate_rotational_force() * Temperature

                # Calculate repulsive force between agent and wall
                if not self.boundaries.contains(current_geometric):
                    nearest_point = np.array(
                        self.boundaries.exterior.interpolate(self.boundaries.exterior.project(current_geometric.centroid)).coords[
                            0
                        ]
                    )
                    force += Crowd.calculate_repulsive_force(current_centroid, nearest_point) * 0.1
                current_agent.rotate(rotational_force)
                # Apply force to agent position if non-zero and within bounds
                if np.linalg.norm(force) > 0:
                    new_position = current_centroid + force
                    if self.boundaries.contains(Point(new_position)):
                        current_agent.translate(force[0], force[1])
            Temperature -= 0.1  # Decrease the temperature at each iteration
            Temperature = max(0.0, Temperature)
