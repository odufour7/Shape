"""Contains functions to download and prepare the data."""

import logging
from pathlib import Path
from typing import get_args

import numpy as np
import pandas as pd
from shapely.geometry import MultiPolygon

import configuration.utils.constants as cst
import configuration.utils.functions as fun
from configuration.utils.typing_custom import Sex


def read_anthropometric_data(sex: Sex, data_dir_path: Path) -> pd.DataFrame:
    """
    Read and process anthropometric data from a sex-specific CSV file.

    Parameters
    ----------
    sex : Sex
        The sex of the individuals whose data is to be read ("male" or "female").
    data_dir_path : Path
        Path to the root data directory containing the "csv" subdirectory.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame containing:
        - Original data with standardized units (converted to cm/kg)
        - Renamed columns with units in brackets
        - Added "sex" column indicating the subject"s gender

    Raises
    ------
    ValueError
        If the provided `sex` is not "male" or "female".
    FileNotFoundError
        If the specified CSV file does not exist in the data directory.

    Notes
    -----
    - Performs the following unit conversions:
        * Height: inches → centimeters
        * Weight: pounds → kilograms
        * Chest depth: millimeters → centimeters
        * Bideltoid breadth: millimeters → centimeters
    - Original column names are renamed to include units in brackets
    """
    # Check if the sex is valid
    if sex not in get_args(Sex):
        raise ValueError("The sex should be either 'male' or 'female'.")

    # Read the CSV file
    dir_path = data_dir_path / "csv"
    file_name = f"ANSURII{sex.upper()}Public.csv"
    df = pd.read_csv(dir_path / file_name, encoding="latin1")

    # Add a column sex
    df["sex"] = np.full_like(df["Heightin"], sex, dtype=object)

    # Standardize units and rename columns
    df["chestdepth"] = df["chestdepth"] * cst.MM_TO_CM  # Convert mm to cm
    df.rename(columns={"chestdepth": "chest depth [cm]"}, inplace=True)
    df["bideltoidbreadth"] = df["bideltoidbreadth"] * cst.MM_TO_CM  # Convert mm to cm
    df.rename(columns={"bideltoidbreadth": "bideltoid breadth [cm]"}, inplace=True)
    df["Heightin"] = df["Heightin"] * cst.INCH_TO_CM  # Convert inches to cm
    df.rename(columns={"Heightin": "height [cm]"}, inplace=True)
    df = df[df["Weightlbs"] != 0]  # Remove rows with zero weight
    df["Weightlbs"] = df["Weightlbs"] * cst.LB_TO_KG  # Keep weight in kg
    df.rename(columns={"Weightlbs": "weight [kg]"}, inplace=True)

    return df


def prepare_anthropometric_data(data_dir_path: Path) -> None:
    """
    Prepare and save anthropometric data as a pickle file.

    This function reads anthropometric data for both males and females,
    combines them into a single DataFrame, and saves the result as a
    pickle file for efficient future access.

    Parameters
    ----------
    data_dir_path : Path
        The path to the root data directory containing input data and
        where the output pickle file will be saved.
    """
    dir_path = data_dir_path / "pkl"
    df_male = read_anthropometric_data("male", data_dir_path)
    df_female = read_anthropometric_data("female", data_dir_path)
    df = pd.concat([df_male, df_female], ignore_index=True)
    fun.save_pickle(df, dir_path / "ANSUREIIPublic.pkl")


def prepare_bike_data(data_dir_path: Path) -> None:
    """
    Prepare bike data by reading a CSV file, processing it, and saving as a pickle file.

    Parameters
    ----------
    data_dir_path : Path
        The path to the root data directory containing "csv" and "pkl" subdirectories.

    Raises
    ------
    FileNotFoundError
        If the specified CSV file does not exist in the data directory.
    """
    df = pd.read_csv(data_dir_path / "csv" / "geometrics.mtb-news.de.csv", sep=";")
    fun.save_pickle(df, data_dir_path / "pkl" / "bike_data.pkl")


def prepare_data() -> None:
    """
    Prepare the data for the application by processing anthropometric and bike data.

    This function checks for the existence of preprocessed data files and, if not found,
    initiates the data preparation process. It performs the following steps:
    1. Prepares anthropometric data by calling `prepare_anthropometric_data()`.
    2. Prepares bike data by calling `prepare_bike_data()`.
    """
    data_dir_path = Path(__file__).parent.parent.parent.parent.absolute() / "data"
    if (
        not (data_dir_path / "pkl" / "bike_data.pkl").exists()
        or not (data_dir_path / "pkl" / "ANSUREIIPublic.pkl").exists()
        or not (data_dir_path / "pkl" / "male_3dBody_light.pkl").exists()
        or not (data_dir_path / "pkl" / "female_3dBody_light.pkl").exists()
    ):
        logging.info("Preparing anthropometric data and bike data...")
        prepare_anthropometric_data(data_dir_path)
        prepare_bike_data(data_dir_path)
        logging.info("Preparing 3D body data...")
        prepare_3D_body_data(data_dir_path)
        logging.info("Data prepared successfully")


def prepare_3D_body_data(data_dir_path: Path) -> None:
    """
    Prepare 3D body data by filtering 3D body shapes to one entry per 3cm bin and saving the filtered data as a new pickle file.

    Parameters
    ----------
    data_dir_path : Path
        The path to the root data directory containing "pkl" subdirectory among others.

    Raises
    ------
    FileNotFoundError
        If the required pickle file does not exist in the data directory.
    """
    for sex in cst.Sex:
        pickle_path = data_dir_path / "pkl" / f"{sex.name}_3dBody.pkl"
        if not pickle_path.exists():
            raise FileNotFoundError(f"Pickle file not found: {pickle_path}")

        shapes3D: dict[float, MultiPolygon] = fun.load_pickle(str(pickle_path))
        keys = sorted(float(k) for k in shapes3D.keys())
        if not keys:
            continue

        target_keys = np.arange(0.0, keys[-1] + 1, cst.DISTANCE_BTW_TARGET_KEYS_ALTITUDES)
        filtered_shapes3D: dict[float, MultiPolygon] = {}
        used_bins = set()

        for key in keys:
            bin_idx = np.argmin(np.abs(target_keys - key))
            bin_value = target_keys[bin_idx]
            if bin_value not in used_bins:
                filtered_shapes3D[key] = MultiPolygon(
                    [geom.simplify(tolerance=cst.POLYGON_TOLERANCE, preserve_topology=True) for geom in shapes3D[key].geoms]
                )
                used_bins.add(bin_value)

        output_path = data_dir_path / "pkl" / f"{sex.name}_3dBody_light.pkl"
        fun.save_pickle(filtered_shapes3D, output_path)
