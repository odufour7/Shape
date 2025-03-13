"""Contains functions to download and prepare the data."""

import logging
from pathlib import Path
from typing import get_args

import numpy as np
import pandas as pd

import src.utils.constants as cst
import src.utils.functions as fun
from src.utils.typing_custom import Sex


def read_anthropometric_data(sex: Sex) -> pd.DataFrame:
    """Read anthropometric data from a CSV file and return it as a pandas DataFrame.

    Parameters
    ----------
    sex : Sex
        The sex of the individuals whose data is to be read. Must be either 'male' or 'female'.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the anthropometric data with standardized units and renamed columns.

    Raises
    ------
    ValueError
        If the provided `sex` is not 'male' or 'female'.

    """
    # Check if the sex is valid
    if sex not in get_args(Sex):
        raise ValueError("The sex should be either 'male' or 'female'.")

    # Read the CSV file
    dir_path = Path(__file__).parent.parent.parent.absolute() / "data" / "csv"
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

    return df


def prepare_anthropometric_data() -> None:
    """Save the anthropometry data as a pickle file.

    This function reads anthropometric data for both male and female,
    concatenates the data into a single DataFrame, and saves it as a
    pickle file in the specified directory.

    Returns
    -------
        None

    """
    dir_path = Path(__file__).parent.parent.parent.absolute() / "data" / "pkl"
    df_male = read_anthropometric_data("male")
    df_female = read_anthropometric_data("female")
    df = pd.concat([df_male, df_female], ignore_index=True)
    fun.save_pickle(df, dir_path / "ANSUREIIPublic.pkl")


def prepare_bike_data() -> None:
    """Prepare bike data by reading a CSV file and saving it as a pickle file.

    This function reads bike data from a CSV file located in the 'data/csv' directory,
    processes it, and saves it as a pickle file in the 'data/pkl' directory.

    Returns
    -------
        None

    """
    dir_path = Path(__file__).parent.parent.parent.absolute() / "data"
    df = pd.read_csv(dir_path / "csv" / "geometrics.mtb-news.de.csv", sep=";")
    fun.save_pickle(df, dir_path / "pkl" / "bike_data.pkl")


def prepare_data() -> None:
    """Prepare the data for the application by calling the necessary data preparation functions.

    This function performs the following steps:
    1. Prepares anthropometric data by calling `prepare_anthropometric_data()`.
    2. Prepares bike data by calling `prepare_bike_data()`.
    3. Prints a success message indicating that the data has been prepared.

    Returns
    -------
        None

    """
    prepare_anthropometric_data()
    prepare_bike_data()
    logging.info("Data prepared successfully")
