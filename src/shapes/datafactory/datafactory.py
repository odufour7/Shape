"""Contains functions to download and prepare the data."""

import logging
from pathlib import Path
from typing import get_args

import numpy as np
import pandas as pd

import shapes.utils.constants as cst
import shapes.utils.functions as fun
from shapes.utils.typing_custom import Sex


def read_anthropometric_data(sex: Sex, data_dir_path: Path) -> pd.DataFrame:
    """
    Read and process anthropometric data from a sex-specific CSV file.

    Parameters
    ----------
    sex : Literal["male","female"]
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

    Examples
    --------
    >>> from pathlib import Path
    >>> data_path = Path("/path/to/data/directory")
    >>> male_data = read_anthropometric_data("male", data_path)
    >>> female_data = read_anthropometric_data("female", data_path)
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
    df["Weightlbs"] = df["Weightlbs"] * cst.LB_TO_KG  # Keep weight in kg
    df.rename(columns={"Weightlbs": "weight [kg]"}, inplace=True)
    print(df["weight [kg]"])

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

    This function reads bike data from a specific CSV file, processes it,
    and saves the resulting DataFrame as a pickle file for faster future access.

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

    Examples
    --------
    >>> prepare_data()
    # If data files don"t exist, this will prepare the data and log a success message.
    # If data files already exist, no action will be taken.
    """
    data_dir_path = Path(__file__).parent.parent.parent.parent.absolute() / "data"
    if not (data_dir_path / "pkl" / "bike_data.pkl").exists() or not (data_dir_path / "pkl" / "ANSUREIIPublic.pkl").exists():
        prepare_anthropometric_data(data_dir_path)
        prepare_bike_data(data_dir_path)
        logging.info("Data prepared successfully")
