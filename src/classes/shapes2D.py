"""Class to store body shapes dynamically based on agent type."""

from dataclasses import dataclass, field
from typing import get_args

import numpy as np
from scipy.optimize import dual_annealing
from shapely.affinity import scale
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

import src.utils.constants as cst
from src.classes.initial_agents import InitialBike, InitialPedestrian
from src.classes.measures import AgentMeasures
from src.utils.typing_custom import AgentType, SapeDataType, ShapeType


@dataclass
class Shapes2D:
    """
    Class to store body shapes dynamically based on agent type.
       - Either you provide a dictionary of shapely shapes as input
       - or you specify the type of shape and its characteristics to create it dynamically.
    """

    agent_type: AgentType
    shapes: SapeDataType = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the provided shapes."""
        if self.agent_type not in get_args(AgentType):
            allowed_values = ", ".join(get_args(AgentType))
            raise ValueError(f"Agent type should be one of: {allowed_values}.")
        if not isinstance(self.shapes, dict):
            raise ValueError("shapes should be a dictionary.")
        # Validate that the provided shapes are valid Shapely objects
        for shape_name, shape in self.shapes.items():
            if not isinstance(shape.get("object"), (Point, Polygon)):
                raise ValueError(
                    f"Invalid shape type for '{shape_name}': {type(shape.get('object'))}"
                )

    def create_shape(
        self, name: str, shape_type: str, young_modulus: float, **kwargs
    ) -> None:
        """
        Dynamically create a shape based on the specified type and characteristics.

        Args:
            name (str): The name of the shape.
            shape_type (str): The type of shape to create ('circle', 'rectangle', or 'polygon').
            young_modulus (float): Material property associated with the shape.
            **kwargs: Additional parameters required to create the specific shape.

        Raises:
            ValueError: If the shape type or required parameters are invalid.
        """
        if shape_type == cst.ShapeTypes.circle.name:
            center = kwargs.get("center")
            radius = kwargs.get("radius")
            if not isinstance(center, tuple) or not isinstance(radius, (int, float)):
                raise ValueError(
                    "For a circle, 'center' must be a tuple and 'radius' must be a number."
                )
            self.shapes[name] = {
                "shape_type": cst.ShapeTypes.circle.name,
                "young_modulus": young_modulus,
                "object": Point(center).buffer(radius),
            }

        elif shape_type == cst.ShapeTypes.rectangle.name:
            min_x = kwargs.get("min_x")
            min_y = kwargs.get("min_y")
            max_x = kwargs.get("max_x")
            max_y = kwargs.get("max_y")
            if not all(
                isinstance(coord, (int, float))
                for coord in [min_x, min_y, max_x, max_y]
            ):
                raise ValueError(
                    "For a rectangle, 'min_x', 'min_y', 'max_x', and 'max_y' must be numbers."
                )
            self.shapes[name] = {
                "shape_type": cst.ShapeTypes.rectangle.name,
                "young_modulus": young_modulus,
                "object": Polygon(
                    [(min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y)]
                ),
            }

        elif shape_type == cst.ShapeTypes.polygon.name:
            points = kwargs.get("points")
            if not isinstance(points, list) or not all(
                isinstance(point, tuple) for point in points
            ):
                raise ValueError("For a polygon, 'points' must be a list of tuples.")

            if len(points) < 3 or points[0] != points[-1]:
                raise ValueError(
                    "A polygon must have at least 3 points and the first/last points must match."
                )

            self.shapes[name] = {
                "shape_type": cst.ShapeTypes.polygon.name,
                "young_modulus": young_modulus,
                "object": Polygon(points),
            }

        else:
            raise ValueError(f"Unsupported shape type: {shape_type}")

    def get_shape(self, name: str) -> dict[str, ShapeType | float | Polygon]:
        """Retrieve a shape by its name."""
        if name not in self.shapes:
            raise KeyError(f"No shape found with name '{name}'.")
        return self.shapes[name]["object"]

    def get_additional_parameters(self) -> SapeDataType:
        """Retrieve additional parameters for each stored shape."""
        params = {}
        for name, shape in self.shapes.items():
            if shape["shape_type"] == cst.ShapeTypes.circle.name:
                disk = shape["object"]
                disk_center = disk.centroid
                disk_radius = disk.exterior.distance(disk.centroid)
                params[name] = {
                    "shape_type": cst.ShapeTypes.circle.name,
                    "young_modulus": shape["young_modulus"],
                    "center": (disk_center.x, disk_center.y),
                    "radius": disk_radius,
                }
            elif shape["shape_type"] == cst.ShapeTypes.rectangle.name:
                rect = shape["object"]
                min_x, min_y, max_x, max_y = rect.bounds
                params[name] = {
                    "shape_type": cst.ShapeTypes.rectangle.name,
                    "young_modulus": shape["young_modulus"],
                    "min_x": min_x,
                    "min_y": min_y,
                    "max_x": max_x,
                    "max_y": max_y,
                }
            elif shape["shape_type"] == cst.ShapeTypes.polygon.name:
                poly = shape["object"]
                poly_points = list(poly.exterior.coords)
                params[name] = {
                    "shape_type": cst.ShapeTypes.polygon.name,
                    "young_modulus": shape["young_modulus"],
                    "points": poly_points,
                }

        return params

    def number_of_shapes(self) -> int:
        """Return the total number of stored shapes."""
        return len(self.shapes)

    def create_pedestrian_shapes(self, measurements: AgentMeasures) -> None:
        """Create the shapes of a pedestrian based on the provided measures."""
        if self.agent_type != cst.AgentTypes.pedestrian.name:
            raise ValueError(
                "create_pedestrian_shapes() can only create pedestrian agents."
            )

        initial_pedestrian = InitialPedestrian(
            measurements.measures[cst.PedestrianParts.sex.name]
        )
        homothety_center = initial_pedestrian.calculate_position()

        def objectif_fun(scaling_factor: np.ndarray) -> float:
            scale_factor_x, scale_factor_y = scaling_factor
            adjusted_centers = [
                scale(disk_center, xfact=scale_factor_x, origin=homothety_center)
                for disk_center in initial_pedestrian.get_disk_centers()
            ]
            adjusted_radii = [
                disk_radius * scale_factor_y
                for disk_radius in initial_pedestrian.get_disk_radii()
            ]
            old_chest_depth = measurements.measures[
                cst.PedestrianParts.chest_depth.name
            ]
            old_bideltoid_breadth = measurements.measures[
                cst.PedestrianParts.bideltoid_breadth.name
            ]
            new_chest_depth = 2.0 * adjusted_radii[2]
            new_bideltoid_breadth = (
                2.0 * adjusted_centers[4].x + 2.0 * adjusted_radii[4]
            )
            penalty_chest = (new_chest_depth - old_chest_depth) ** 2
            penalty_shoulder_breadth = (
                new_bideltoid_breadth - old_bideltoid_breadth
            ) ** 2
            return penalty_chest + penalty_shoulder_breadth

        bounds = np.array([[1e-5, 3.0], [1e-5, 3.0]])
        guess_parameters = np.array([0.9, 0.9])
        optimized_scaling = dual_annealing(
            objectif_fun,
            bounds=bounds,
            maxiter=100,
            x0=guess_parameters,
            # minimizer_kwargs={"method": "Nelder-Mead", "tol": 0.001},
        )
        optimized_scale_factor_x, optimized_scale_factor_y = optimized_scaling.x
        # Adjust centers of disks
        adjusted_centers = [
            scale(disk_center, xfact=optimized_scale_factor_x, origin=homothety_center)
            for disk_center in initial_pedestrian.get_disk_centers()
        ]
        adjusted_radii = [
            disk_radius * optimized_scale_factor_y
            for disk_radius in initial_pedestrian.get_disk_radii()
        ]
        disks = [
            {"center": center, "radius": radius}
            for center, radius in zip(adjusted_centers, adjusted_radii)
        ]
        adjusted_shapes = {
            f"disk{i}": {
                "shape_type": cst.ShapeTypes.circle.name,
                "young_modulus": cst.YOUNG_MODULUS_DISK_INIT,
                "object": Point(disk["center"]).buffer(disk["radius"]),
            }
            for i, disk in enumerate(disks)
        }

        self.shapes = adjusted_shapes

    def create_bike_shapes(self, measurements: AgentMeasures) -> None:
        """Create the shapes of a bike based on the provided measures."""
        if self.agent_type != cst.AgentTypes.bike.name:
            raise ValueError("create_bike_shapes() can only create bike agents.")

        init_bike = InitialBike()

        def objective_fun(scaling_factor: np.ndarray) -> float:
            """Objective function to minimize the difference between the wanted and actual bike/rider dimensions."""
            (
                scale_bike_factor_x,
                scale_bike_factor_y,
                scale_rider_factor_x,
                scale_rider_factor_y,
            ) = scaling_factor
            new_shapes = {
                "bike": {
                    "shape_type": cst.ShapeTypes.rectangle.name,
                    "young_modulus": cst.YOUNG_MODULUS_RECTANGLE_INIT,
                    "min_x": init_bike.shapes["bike"]["min_x"] * scale_bike_factor_x,
                    "min_y": init_bike.shapes["bike"]["min_y"] * scale_bike_factor_y,
                    "max_x": init_bike.shapes["bike"]["max_x"] * scale_bike_factor_x,
                    "max_y": init_bike.shapes["bike"]["max_y"] * scale_bike_factor_y,
                },
                "rider": {
                    "shape_type": cst.ShapeTypes.rectangle.name,
                    "young_modulus": cst.YOUNG_MODULUS_RECTANGLE_INIT,
                    "min_x": init_bike.shapes["rider"]["min_x"] * scale_rider_factor_x,
                    "min_y": init_bike.shapes["rider"]["min_y"] * scale_rider_factor_y,
                    "max_x": init_bike.shapes["rider"]["max_x"] * scale_rider_factor_x,
                    "max_y": init_bike.shapes["rider"]["max_y"] * scale_rider_factor_y,
                },
            }
            wanted_rider_width = measurements.measures[
                cst.BikeParts.handlebar_length.name
            ]
            wanted_rider_length = measurements.measures[
                cst.BikeParts.top_tube_length.name
            ]
            wanted_bike_width = measurements.measures[cst.BikeParts.wheel_width.name]
            wanted_bike_length = measurements.measures[cst.BikeParts.total_length.name]
            current_bike_length = abs(
                new_shapes["bike"]["max_y"] - new_shapes["bike"]["min_y"]
            )
            current_rider_width = abs(
                new_shapes["rider"]["max_x"] - new_shapes["rider"]["min_x"]
            )
            current_rider_length = abs(
                new_shapes["rider"]["max_y"] - new_shapes["rider"]["min_y"]
            )
            current_bike_width = abs(
                new_shapes["bike"]["max_x"] - new_shapes["bike"]["min_x"]
            )
            penalty_rider_width = (wanted_rider_width - current_rider_width) ** 2
            penalty_rider_length = (wanted_rider_length - current_rider_length) ** 2
            penalty_bike_width = (wanted_bike_width - current_bike_width) ** 2
            penalty_bike_length = (wanted_bike_length - current_bike_length) ** 2
            return (
                penalty_rider_length
                + penalty_bike_width
                + penalty_bike_length
                + penalty_rider_width
            )

        bounds = np.array([[1e-5, 3.0], [1e-5, 3.0], [1e-5, 3.0], [1e-5, 3.0]])
        guess_parameters = np.array([0.99, 0.99, 0.99, 0.99])
        optimised_scaling = dual_annealing(
            objective_fun,
            bounds=bounds,
            maxiter=100,
            x0=guess_parameters,
        )
        opt_bike_sfx, opt_bike_sfy, opt_rider_sfx, opt_rider_sfy = (
            optimised_scaling.x
        )  # optimised scaling factors
        adjusted_shapes = {
            "bike": {
                "shape_type": cst.ShapeTypes.rectangle.name,
                "young_modulus": cst.YOUNG_MODULUS_RECTANGLE_INIT,
                "object": Polygon(
                    [
                        (
                            init_bike.shapes["bike"]["min_x"] * opt_bike_sfx,
                            init_bike.shapes["bike"]["min_y"] * opt_bike_sfy,
                        ),
                        (
                            init_bike.shapes["bike"]["min_x"] * opt_bike_sfx,
                            init_bike.shapes["bike"]["max_y"] * opt_bike_sfy,
                        ),
                        (
                            init_bike.shapes["bike"]["max_x"] * opt_bike_sfx,
                            init_bike.shapes["bike"]["max_y"] * opt_bike_sfy,
                        ),
                        (
                            init_bike.shapes["bike"]["max_x"] * opt_bike_sfx,
                            init_bike.shapes["bike"]["min_y"] * opt_bike_sfy,
                        ),
                    ]
                ),
            },
            "rider": {
                "shape_type": cst.ShapeTypes.rectangle.name,
                "young_modulus": cst.YOUNG_MODULUS_RECTANGLE_INIT,
                "object": Polygon(
                    [
                        (
                            init_bike.shapes["rider"]["min_x"] * opt_rider_sfx,
                            init_bike.shapes["rider"]["min_y"] * opt_rider_sfy,
                        ),
                        (
                            init_bike.shapes["rider"]["min_x"] * opt_rider_sfx,
                            init_bike.shapes["rider"]["max_y"] * opt_rider_sfy,
                        ),
                        (
                            init_bike.shapes["rider"]["max_x"] * opt_rider_sfx,
                            init_bike.shapes["rider"]["max_y"] * opt_rider_sfy,
                        ),
                        (
                            init_bike.shapes["rider"]["max_x"] * opt_rider_sfx,
                            init_bike.shapes["rider"]["min_y"] * opt_rider_sfy,
                        ),
                    ]
                ),
            },
        }
        self.shapes = adjusted_shapes

    def get_geometric_shape(self) -> Polygon:
        """Return the union geometry of the stored shapes."""
        return unary_union([shape["object"] for shape in self.shapes.values()])
