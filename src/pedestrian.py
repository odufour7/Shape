""" This module contains functions to load and process data, as well as classes to represent pedestrians. """

import numpy as np
import pandas as pd
from shapely.affinity import rotate, scale, translate
from shapely.geometry import MultiPolygon, Point, Polygon
from shapely.ops import unary_union

import utils.constants as cst
import utils.functions as fun
from utils.typing_custom import Sex


class InitialState:
    """Encapsulates the initial pedestrian state."""

    def __init__(self, sex: Sex) -> None:
        """Initializes the initial state with shape data and derived constants."""

        if sex not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")

        self._sex: Sex = sex
        self._dataframe_shape: pd.DataFrame = pd.DataFrame(
            {
                "radius [cm]": np.array([282.41232, 388.36243, 405.97552, 388.36243, 282.41232]) * cst.PIXEL_TO_CM,
                "x [cm]": np.array([-552.7920, -242.5697, 0.0000, 242.5697, 552.7920]) * cst.PIXEL_TO_CM,
                "y [cm]": np.array([0.00000, 71.73901, 86.11438, 71.73901, 0.00000]) * cst.PIXEL_TO_CM,
            }
        )
        self._bideltoid_breadth: float = (
            2.0 * self._dataframe_shape["x [cm]"].iloc[-1] + 2.0 * self._dataframe_shape["radius [cm]"].iloc[-1]
        )
        self._chest_depth: float = 2.0 * self._dataframe_shape["radius [cm]"].iloc[2]
        self._body3D: dict[int, Polygon] = fun.load_pickle(cst.PICKLE_DIR / f"{sex}_3dBody.pkl")
        self._height: float = abs(max(self._body3D.keys()) - min(self._body3D.keys()))

    @property
    def sex(self) -> Sex:
        """Returns the sex."""
        return self._sex

    @property
    def height(self) -> float:
        """Returns the initial height of the pedestrian."""
        return self._height

    @property
    def dataframe_shape(self) -> pd.DataFrame:
        """Returns the initial shape data as a DataFrame."""
        return self._dataframe_shape

    @property
    def bideltoid_breadth(self) -> float:
        """Returns the initial bideltoid breadth constant."""
        return self._bideltoid_breadth

    @property
    def chest_depth(self) -> float:
        """Returns the initial chest depth constant."""
        return self._chest_depth

    @property
    def body3D(self) -> dict[int, MultiPolygon]:
        """Returns the 3D body of the pedestrian."""
        return self._body3D


class Pedestrian:
    """Represents a pedestrian with specific chest depth and bideltoid breadth."""

    def __init__(
        self,
        chest_depth: float,
        bideltoid_breadth: float,
        height: float = 1.8,
        sex: Sex = "male",
        young_modulus: float = 2.5e6,
    ) -> None:
        """Initializes a Pedestrian object."""

        if chest_depth <= 0 or bideltoid_breadth <= 0 or height <= 0:
            raise ValueError("Chest depth and bideltoid breadth must be positive values.")
        if sex not in ["male", "female"]:
            raise ValueError("The sex should be either 'male' or 'female'.")
        if young_modulus <= 0:
            raise ValueError("Young modulus must be a strictly positive value.")

        self._chest_depth: float = chest_depth
        self._bideltoid_breadth: float = bideltoid_breadth
        self._height: float = height
        self._sex: Sex = sex
        self._young_modulus: float = young_modulus

        self._initial_state: InitialState = InitialState(sex)

        self._dataframe_shape: pd.DataFrame = self.calculate_dataframe_shape()
        self._body3D: dict[int, MultiPolygon] = self.calculate_body3D()

    @property
    def chest_depth(self) -> float:
        """Get the chest depth of the pedestrian."""
        return self._chest_depth

    @chest_depth.setter
    def chest_depth(self, value: float) -> None:
        """Set a new chest depth for the pedestrian."""
        if value <= 0:
            raise ValueError("Chest depth must be a positive value.")
        self._chest_depth = value

    @property
    def bideltoid_breadth(self) -> float:
        """Get the bideltoid breadth of the pedestrian."""
        return self._bideltoid_breadth

    @bideltoid_breadth.setter
    def bideltoid_breadth(self, value: float) -> None:
        """Set a new bideltoid breadth for the pedestrian."""
        if value <= 0:
            raise ValueError("Bideltoid breadth must be a positive value.")
        self._bideltoid_breadth = value

    @property
    def height(self) -> float:
        """Get the height of the pedestrian."""
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        """Set a new height for the pedestrian."""
        if value <= 0:
            raise ValueError("Height must be a positive value.")
        self._height = value

    @property
    def sex(self) -> Sex:
        """Get the sex of the pedestrian."""
        return self._sex

    @sex.setter
    def sex(self, value: str) -> None:
        """Set a new sex for the pedestrian."""
        if value not in ["male", "female"]:
            raise ValueError("Sex should be either 'male' or 'female'.")
        self._sex = value

    @property
    def young_modulus(self) -> float:
        """Returns the Young modulus of the pedestrian."""
        return self._young_modulus

    @young_modulus.setter
    def young_modulus(self, value: float) -> None:
        """Set a new Young modulus for the pedestrian."""
        if value <= 0:
            raise ValueError("Young modulus must be a positive value.")
        self._young_modulus = value

    @property
    def initial_state(self) -> InitialState:
        """Get the initial state of the pedestrian."""
        return self._initial_state

    @property
    def dataframe_shape(self) -> pd.DataFrame:
        """Get the DataFrame representing the pedestrian shape."""
        return self._dataframe_shape

    @dataframe_shape.setter
    def dataframe_shape(self, value: pd.DataFrame) -> None:
        """Set a new DataFrame representing the pedestrian shape."""
        self._dataframe_shape = value

    @property
    def body3D(self) -> dict[int, MultiPolygon]:
        """Get the 3D body of the pedestrian."""
        return self._body3D

    @body3D.setter
    def body3D(self, value: dict[int, MultiPolygon]) -> None:
        """Set a new 3D body for the pedestrian."""
        self._body3D = value

    def calculate_dataframe_shape(self) -> pd.DataFrame:
        """Adjusts the shape of the pedestrian based on chest depth and bideltoid breadth."""
        scale_factor_x = self.bideltoid_breadth / self.initial_state.bideltoid_breadth
        scale_factor_y = self.chest_depth / self.initial_state.chest_depth
        df_init_shape = self.initial_state.dataframe_shape
        homothety_center = Point(df_init_shape["x [cm]"].iloc[2], df_init_shape["y [cm]"].iloc[4])

        # Create initial disks
        disks = [
            Point(x, y).buffer(r, resolution=100)
            for x, y, r in zip(
                df_init_shape["x [cm]"],
                df_init_shape["y [cm]"],
                df_init_shape["radius [cm]"],
            )
        ]

        # Adjust disks by scaling
        adjusted_disks = [scale(circle, xfact=scale_factor_y, yfact=scale_factor_y, origin=homothety_center) for circle in disks]

        # Adjust centers of disks
        adjusted_centers = [scale(disk.centroid, xfact=scale_factor_x, origin=homothety_center) for disk in adjusted_disks]

        # Create a DataFrame for the adjusted shape
        df_pedestrian = pd.DataFrame(
            {
                "radius [cm]": [disk.exterior.distance(disk.centroid) for disk in adjusted_disks],
                "x [cm]": [center.x for center in adjusted_centers],
                "y [cm]": [center.y for center in adjusted_centers],
            }
        )

        return df_pedestrian

    def calculate_position(self) -> tuple[float, float]:
        """Returns the position of the pedestrian."""
        df_shape = self.dataframe_shape
        return df_shape["x [cm]"].iloc[2], df_shape["y [cm]"].iloc[2]

    def calculate_geometric_shape(self) -> Polygon:
        """Create a geometric agent shape based on the provided agent shape DataFrame."""
        df_shape = self.dataframe_shape
        circles = [
            Point(df_shape.loc[i, "x [cm]"], df_shape.loc[i, "y [cm]"]).buffer(df_shape.loc[i, "radius [cm]"], resolution=100)
            for i in range(cst.DISK_NUMBER)
        ]

        return unary_union(circles)

    def translate_shape(self, x_translation: float, y_translation: float) -> pd.DataFrame:
        """Translate the pedestrian shape by the given x and y translations."""
        df_shape = self.dataframe_shape
        df_shape["x [cm]"] += x_translation
        df_shape["y [cm]"] += y_translation
        return df_shape

    def rotate_shape(self, angle: float) -> pd.DataFrame:
        """Rotate the shape around its center of mass (CM) of an angle theta in radian."""
        shape_CM = self.calculate_position()
        df_shape = self.dataframe_shape
        # translate shape to the origin
        df_shape["x [cm]"] -= shape_CM[0]
        df_shape["y [cm]"] -= shape_CM[1]
        # rotate shape
        df_shape["x_rotated"] = df_shape["x [cm]"].copy() * np.cos(angle) - df_shape["y [cm]"].copy() * np.sin(angle)
        df_shape["y_rotated"] = df_shape["x [cm]"].copy() * np.sin(angle) + df_shape["y [cm]"].copy() * np.cos(angle)
        df_shape.drop(columns=["x [cm]", "y [cm]"], inplace=True)
        df_shape.rename(columns={"x_rotated": "x [cm]", "y_rotated": "y [cm]"}, inplace=True)
        # translate shape back to the original position
        df_shape["x [cm]"] += shape_CM[0]
        df_shape["y [cm]"] += shape_CM[1]
        return df_shape

    @staticmethod
    def calculate_body_vertical_axis(body3D: dict[int, MultiPolygon]) -> Point:
        """Calculates the vertical axis of the pedestrian's body."""
        # Extract centroids from MultiPolygon objects in body3D
        centroids = [multipolygon.centroid for multipolygon in body3D.values()]

        # Ensure all centroids are valid Shapely Point objects
        if not all(isinstance(p, Point) for p in centroids):
            raise TypeError("All centroids must be Shapely Point objects.")

        # Calculate mean coordinates for x, y, and z axes
        mean_x = np.mean([p.x for p in centroids if not p.is_empty])
        mean_y = np.mean([p.y for p in centroids if not p.is_empty])

        return Point(mean_x, mean_y)

    def calculate_body3D(self) -> dict[int, MultiPolygon]:
        """Returns the 3D body of the pedestrian."""
        scale_factor_x = self.bideltoid_breadth / self.initial_state.bideltoid_breadth
        scale_factor_y = self.chest_depth / self.initial_state.chest_depth
        scale_factor_z = self.height / self.initial_state.height

        current_body3D = {}
        homothety_center = Pedestrian.calculate_body_vertical_axis(self.initial_state.body3D)
        for height, multipolygon in self.initial_state.body3D.items():
            scaled_multipolygon = scale(multipolygon, xfact=scale_factor_x, yfact=scale_factor_y, origin=homothety_center)
            scaled_height = height * scale_factor_z
            current_body3D[scaled_height] = scaled_multipolygon

        return current_body3D

    def translate_body3D(self, dx: float, dy: float, dz: float) -> dict[int, MultiPolygon]:
        """Translates the 3D body of the pedestrian by the specified displacements dx, dy, and dz."""
        translated_body3D = {}
        for height, multipolygon in self.body3D.items():
            translated_body3D[height + dz] = translate(multipolygon, dx, dy)
        return translated_body3D

    def rotate_body3D(self, angle: float) -> dict[int, MultiPolygon]:
        """Rotates the 3D body of the pedestrian by the specified angle in radian."""
        rotated_body3D = {}
        centroid_body = Pedestrian.calculate_body_vertical_axis(self.body3D)
        for height, multipolygon in self.body3D.items():
            rotated_body3D[height] = rotate(multipolygon, angle, origin=centroid_body, use_radians=True)
        return rotated_body3D
