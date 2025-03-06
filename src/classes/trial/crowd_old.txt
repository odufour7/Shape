"""Crowd class definition and example usage."""

import numpy as np
from scipy.stats import truncnorm
from shapely.geometry import Point, Polygon

import src.utils.constants as cst
from src.classes.trial.pedestrian import Pedestrian


class Crowd:
    """Class representing a crowd of pedestrians in a room."""

    def __init__(
        self,
        density: float,
        boundaries: Polygon,
        chest_depth: tuple[float, float] = 35,
        bideltoid_breadth: tuple[float, float] = 42,
    ) -> None:
        # Validate and set attributes using setters
        if not cst.MIN_DENSITY <= density <= cst.MAX_DENSITY:
            raise ValueError(f"Density must be between {cst.MIN_DENSITY} and {cst.MAX_DENSITY}.")
        if not isinstance(boundaries, Polygon) or boundaries.is_empty:
            raise ValueError("Boundaries must be a non-empty Polygon.")
        if not cst.MIN_CHEST_DEPTH <= chest_depth[0] <= cst.MAX_CHEST_DEPTH:
            raise ValueError(f"Mean chest depth must be between {cst.MIN_CHEST_DEPTH} and {cst.MAX_CHEST_DEPTH}.")
        if not chest_depth[1] >= 0:
            raise ValueError("Standard deviation must be positive.")
        if not cst.MIN_BIDELTOID_BREADTH <= bideltoid_breadth[0] <= cst.MAX_BIDELTOID_BREADTH:
            raise ValueError(
                f"Mean bideltoid breadth must be between {cst.MIN_BIDELTOID_BREADTH} and {cst.MAX_BIDELTOID_BREADTH}."
            )
        if not bideltoid_breadth[1] >= 0.0:
            raise ValueError("Standard deviation must be positive.")

        self._density: float = density
        self._boundaries: Polygon = boundaries
        self._chest_depth: tuple[float, float] = chest_depth
        self._bideltoid_breadth: tuple[float, float] = bideltoid_breadth

        self._packed_crowd: dict[int, Pedestrian] = self.generate_packing_crowd()

    # Density property with getter and setter
    @property
    def density(self) -> float:
        """Density of the crowd in persons per square meter."""
        return self._density

    @density.setter
    def density(self, value) -> None:
        """Setter for the density property."""
        if not cst.MIN_DENSITY <= value <= cst.MAX_DENSITY:
            raise ValueError(f"Density must be between {cst.MIN_DENSITY} and {cst.MAX_DENSITY}.")
        self._density = value
        self._packed_crowd = self.generate_packing_crowd()

    # Boundaries property with getter and setter
    @property
    def boundaries(self) -> Polygon:
        """Boundaries of the space where the crowd is located."""
        return self._boundaries

    @boundaries.setter
    def boundaries(self, value) -> None:
        """Setter for the boundaries property."""
        if not isinstance(value, Polygon) or value.is_empty:
            raise ValueError("The boundaries must be a non-empty Polygon.")
        self._boundaries = value
        self._packed_crowd = self.generate_packing_crowd()

    # Chest depth property with getter and setter
    @property
    def chest_depth(self) -> tuple[float, float]:
        """Mean and standard deviation of the chest depth of the pedestrians in the crowd."""
        return self._chest_depth

    @chest_depth.setter
    def chest_depth(self, value) -> None:
        """Setter for the chest depth property."""
        mean, std_dev = value
        if not cst.MIN_CHEST_DEPTH <= mean <= cst.MAX_CHEST_DEPTH:
            raise ValueError(f"Mean chest depth must be between {cst.MIN_CHEST_DEPTH} and {cst.MAX_CHEST_DEPTH}.")
        if not std_dev >= 0:
            raise ValueError("Standard deviation must be positive.")
        self._chest_depth = value
        self._packed_crowd = self.generate_packing_crowd()

    # Bideltoid breadth property with getter and setter
    @property
    def bideltoid_breadth(self) -> tuple[float, float]:
        """Mean and standard deviation of the bideltoid breadth of the pedestrians in the crowd."""
        return self._bideltoid_breadth

    @bideltoid_breadth.setter
    def bideltoid_breadth(self, value) -> None:
        """Setter for the bideltoid breadth property."""
        mean, std_dev = value
        if not cst.MIN_BIDELTOID_BREADTH <= mean <= cst.MAX_BIDELTOID_BREADTH:
            raise ValueError(
                f"Mean bideltoid breadth must be between {cst.MIN_BIDELTOID_BREADTH} and {cst.MAX_BIDELTOID_BREADTH}."
            )
        if not std_dev >= 0:
            raise ValueError("Standard deviation must be positive.")
        self._bideltoid_breadth = value
        self._packed_crowd = self.generate_packing_crowd()

    # Packed crowd property with getter
    @property
    def packed_crowd(self) -> dict[int, Pedestrian]:
        """Crowd of pedestrians with random chest depth, bideltoid breadth and orientation."""
        return self._packed_crowd

    @packed_crowd.setter
    def packed_crowd(self, value: dict[int, Pedestrian]) -> None:
        """Setter for the packed crowd property."""
        self._packed_crowd = value

    def draw_chest_depth(self) -> float:
        """Draw a random chest depth from a truncated normal distribution."""
        mean, std_dev = self.chest_depth

        # Calculate the 'a' and 'b' parameters for the truncated normal distribution
        a = (cst.MIN_CHEST_DEPTH - mean) / std_dev
        b = (cst.MAX_CHEST_DEPTH - mean) / std_dev

        # Generate a random value from the truncated normal distribution
        return truncnorm.rvs(a, b, loc=mean, scale=std_dev)

    def draw_bideltoid_breadth(self) -> float:
        """Draw a random bideltoid breadth from a truncated normal distribution."""
        mean, std_dev = self.bideltoid_breadth

        # Calculate the 'a' and 'b' parameters for the truncated normal distribution
        a = (cst.MIN_BIDELTOID_BREADTH - mean) / std_dev
        b = (cst.MAX_BIDELTOID_BREADTH - mean) / std_dev

        return truncnorm.rvs(a, b, loc=mean, scale=std_dev)

    def draw_crowd_orientation(self) -> float:
        """Draw a random orientation angle for the crowd from a truncated normal distribution."""
        return 0.0  # np.random.uniform(-np.pi, np.pi)

    def pedestrian_number(self) -> int:
        """Calculate the number of pedestrians in the crowd."""
        return int(self.density * self.boundaries.area)

    def generate_pedestrians(self) -> dict[int, Pedestrian]:
        """Generate a list of pedestrians represented by 2D geometric shapes with random chest depth and bideltoid breadth."""
        pedestrians = {}
        box_center = self.boundaries.centroid
        for count in range(self.pedestrian_number()):
            chest_depth = self.draw_chest_depth()
            bideltoid_breadth = self.draw_bideltoid_breadth()
            crowd_orientation = self.draw_crowd_orientation()
            single_pedestrian = Pedestrian(chest_depth, bideltoid_breadth)
            single_pedestrian.dataframe_shape = single_pedestrian.rotate_shape(crowd_orientation)
            single_pedestrian.dataframe_shape = single_pedestrian.translate_shape(box_center.x, box_center.y)
            pedestrians[count] = single_pedestrian
        return pedestrians

    @staticmethod
    def calculate_repulsive_force(agent_centroid: np.ndarray, other_centroid: np.ndarray) -> np.ndarray:
        """Calculate the repulsive force between two centroids."""
        delta = agent_centroid - other_centroid
        norm_delta = np.linalg.norm(delta)
        if norm_delta != 0:
            return delta / norm_delta
        return np.random.rand(2)  # Small random force if centroids coincide

    @staticmethod
    def apply_forces(
        pedestrians: dict[int, Pedestrian],
        boundaries: Polygon,
    ) -> dict[int, Pedestrian]:
        """Simulates the application of forces on agents within a polygonal cell over a number of iterations."""

        for _ in range(cst.MAX_NB_ITERATIONS):
            # Check for overlaps and apply forces if necessary
            for i_ped, current_ped in pedestrians.items():
                force = np.array([0.0, 0.0])
                current_geometric = current_ped.calculate_geometric_shape()
                current_centroid = np.array(current_geometric.centroid.coords[0])
                # Calculate repulsive force between agents
                for j_ped, neigh_ped in pedestrians.items():
                    neigh_geometric = neigh_ped.calculate_geometric_shape()
                    if i_ped != j_ped and current_geometric.intersects(neigh_geometric):
                        neigh_centroid = np.array(neigh_geometric.centroid.coords[0])
                        force += Crowd.calculate_repulsive_force(current_centroid, neigh_centroid)

                # Calculate repulsive force between agent and wall
                if not boundaries.contains(current_geometric):
                    nearest_point = np.array(
                        boundaries.exterior.interpolate(boundaries.exterior.project(current_geometric.centroid)).coords[0]
                    )
                    force += Crowd.calculate_repulsive_force(current_centroid, nearest_point)

                # Apply force to agent position if non-zero and within bounds
                if np.linalg.norm(force) > 0:
                    new_position = current_centroid + force
                    if boundaries.contains(Point(new_position)):
                        current_ped.dataframe_shape = current_ped.translate_shape(force[0], force[1])

        return pedestrians

    def generate_packing_crowd(self) -> dict[int, Pedestrian]:
        """Generate a crowd of pedestrians with random chest depth, bideltoid breadth and orientation."""
        pedestrians = self.generate_pedestrians()
        packing_crowd = Crowd.apply_forces(pedestrians, self.boundaries)
        return packing_crowd

    def calculate_interpenetration(self) -> float:
        """Calculate the interpenetration area between pedestrians"""
        interpenetration = 0.0

        for i_ped, current_ped in self.packed_crowd.items():
            current_geometric = current_ped.calculate_geometric_shape()
            for j_ped, neigh_ped in self.packed_crowd.items():
                if i_ped > j_ped:
                    neigh_geometric = neigh_ped.calculate_geometric_shape()
                    interpenetration += current_geometric.intersection(neigh_geometric).area
        # conversion to m^2
        interpenetration /= 1e4  # 1 cm^2 = 1e-4 m^2
        return interpenetration
