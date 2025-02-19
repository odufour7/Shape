""" This module reads the anthropometric data from the ANSUR II dataset and saves it as a pandas DataFrame."""

from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

import src.utils.constants as cst
import src.utils.functions as fun
from src.plotting import plot
from src.utils.typing_custom import Sex


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


def main() -> None:
    save_anthropometric_data()
    df = fun.load_pickle(cst.PICKLE_DIR / "ANSUREIIPublic.pkl")

    st.title("Distribution Visualization")
    if st.button("Draw a Distribution"):
        fig = plot.display_disbtribution(df, "Bideltoid breadth [cm]")
        st.pyplot(fig)
        # Save the figure to a BytesIO object in PDF format
        dist_plot = BytesIO()
        fig.savefig(dist_plot, format="pdf")
        dist_plot.seek(0)  # Reset buffer pointer to the beginning
        # Streamlit button in the sidebar to download the graph in PDF format
        st.sidebar.download_button(
            label="Download Image",
            data=dist_plot,
            file_name="distribution.pdf",
            mime="application/pdf",
        )


def run_tab_anthropometry() -> None:
    """
    Execute the main function for the survey tab.

    This function serves as the entry point for running the 2D pedestrian tab
    functionality within the application. It calls the main() function
    to initiate the necessary processes.
    """
    print("here")
    main()
