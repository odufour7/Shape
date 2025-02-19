""" Crowd class definition and example usage. """

import numpy as np
from scipy.stats import truncnorm
from shapely.geometry import Point, Polygon
from tqdm import tqdm

import src.utils.constants as cst
import src.utils.functions as fun
from src.classes.pedestrian import Pedestrian


class Crowd:
    """Class representing a crowd of pedestrians in a room."""

    def __init__(
        self,
        density: float,
        geometry: Polygon,
        chest_depth: tuple[float, float] = 35,
        bideltoid_breadth: tuple[float, float] = 42,
        crowd_orientation: tuple[float, float] = np.pi / 2.0,
    ) -> None:
        # Validate and set attributes using setters
        if not cst.MIN_DENSITY <= density <= cst.MAX_DENSITY:
            raise ValueError(f"Density must be between {cst.MIN_DENSITY} and {cst.MAX_DENSITY}.")
        if not isinstance(geometry, Polygon) or geometry.is_empty:
            raise ValueError("Geometry must be a non-empty Polygon.")
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
        if not -np.pi <= crowd_orientation[0] <= np.pi:
            # vrap the orientation angle to the range -pi to pi
            crowd_orientation[0] = fun.wrap_angle(crowd_orientation)
        if not crowd_orientation[1] >= 0.0:
            raise ValueError("Standard deviation must be positive.")

        self._density: float = density
        self._geometry: Polygon = geometry
        self._chest_depth: tuple[float, float] = chest_depth
        self._bideltoid_breadth: tuple[float, float] = bideltoid_breadth
        self._crowd_orientation: tuple[float, float] = crowd_orientation

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

    # Geometry property with getter and setter
    @property
    def geometry(self) -> Polygon:
        """Geometry of the room where the crowd is located."""
        return self._geometry

    @geometry.setter
    def geometry(self, value) -> None:
        """Setter for the geometry property."""
        if not isinstance(value, Polygon) or value.is_empty:
            raise ValueError("Geometry must be a non-empty Polygon.")
        self._geometry = value

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

    # Crowd orientation property with getter and setter
    @property
    def crowd_orientation(self) -> tuple[float, float]:
        """Mean and standard deviation of the orientation angle of the crowd."""
        return self._crowd_orientation

    @crowd_orientation.setter
    def crowd_orientation(self, value) -> None:
        """Setter for the crowd orientation property."""
        if not -np.pi <= value[0] < np.pi:
            # Wrap the orientation angle to the range [-π to π)
            value[0] = fun.wrap_angle(value[0])
        if not value[1] >= 0:
            raise ValueError("Standard deviation must be positive.")
        self._crowd_orientation = value

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
        # mean, std_dev = self.crowd_orientation

        # Calculate the 'a' and 'b' parameters for the truncated normal distribution
        # a = (-np.pi - mean) / std_dev
        # b = (np.pi - mean) / std_dev
        return np.random.uniform(-np.pi, np.pi)  # return truncnorm.rvs(a, b, loc=mean, scale=std_dev)

    def pedestrian_number(self) -> int:
        """Calculate the number of pedestrians in the crowd."""
        return int(self.density * self.geometry.area)

    def generate_pedestrians(self) -> dict[int, Pedestrian]:
        """Generate a list of pedestrians represented by 2D geometric shapes with random chest depth and bideltoid breadth."""
        pedestrians = {}
        box_center = self.geometry.centroid
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

        for _ in tqdm(range(cst.MAX_NB_ITERATIONS)):
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
        packing_crowd = Crowd.apply_forces(pedestrians, self.geometry)
        return packing_crowd


# # Example usage:
# if __name__ == "__main__":
#     # ajouter une classe anthropometric data pour les valeurs de référence (où on plotte les distriubtions selon les sexes)
#     # ajouter la possibilité de créer une crowd à partir des données anthropométriques en mettant la possibilité
#     # de tirer les valeur depuis les distribution anthropométriques plutôt qu eloi normale
#     room_geometry = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])  # Example room geometry

#     try:
#         crowd = Crowd(
#             density=13e-4,
#             geometry=room_geometry,
#             chest_depth=(15.0, 5.0),
#             bideltoid_breadth=(25.0, 5.0),
#             crowd_orientation=(0.0, 0.5),
#         )

#         print("Crowd successfully created!")

#         print(f"Density: {crowd.density}")
#         print(f"Chest Depth: {crowd.chest_depth}")
#         print(f"Geometry: {crowd.geometry}")
#         print(f"Bideltoid Breadth: {crowd.bideltoid_breadth}")
#         print(f"Crowd Orientation: {crowd.crowd_orientation}")
#         print(f"Number of pedestrians: {crowd.pedestrian_number()}")
#         plot.display_crowd2D(crowd)

#     except ValueError as e:
#         print(f"Error creating crowd: {e}")
