""" This module reads the anthropometric data from the ANSUR II dataset and saves it as a pandas DataFrame."""

import numpy as np
import pandas as pd

import utils.constants as cst
import utils.functions as fun
from utils.typing_custom import Sex


def read_anthropometric_data(sex: Sex) -> None:
    """Read anthropometry data from a csv file and return it as a pandas DataFrame."""
    if sex not in ["male", "female"]:
        raise ValueError("The sex should be either 'male' or 'female'.")

    # Read the CSV file
    file_name = f"ANSURII{sex.upper()}Public.csv"
    df = pd.read_csv(cst.CSV_DIR / file_name, encoding="latin1")

    # Add a column sex
    df["Sex"] = np.full_like(df["Heightin"], sex, dtype=object)

    # Standardize units and rename columns
    df["chestdepth"] = df["chestdepth"] / 10.0  # Convert mm to cm
    df.rename(columns={"chestdepth": "Chest depth [cm]"}, inplace=True)
    df["bideltoidbreadth"] = df["bideltoidbreadth"] / 10.0  # Convert mm to cm
    df.rename(columns={"bideltoidbreadth": "Bideltoid breadth [cm]"}, inplace=True)
    df["Heightin"] = df["Heightin"] * 2.54  # Convert inches to cm
    df.rename(columns={"Heightin": "Height [cm]"}, inplace=True)
    return df


def save_anthropometric_data() -> None:
    """Save the anthropometry data as a pickle file."""
    df_male = read_anthropometric_data("male")
    df_female = read_anthropometric_data("female")
    df = pd.concat([df_male, df_female], ignore_index=True)
    fun.save_pickle(df, cst.PICKLE_DIR / "ANSUREIIPublic.pkl")
