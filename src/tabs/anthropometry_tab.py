"""This module reads the anthropometric data from the ANSUR II dataset and saves it as a pandas DataFrame."""

from pathlib import Path

import streamlit as st

import src.utils.constants as cst
import src.utils.functions as fun
from src.plotting import plot


def main() -> None:
    """Main function for the anthropometry tab."""

    # Load the dataset from a pickle file
    df = fun.load_pickle(cst.PICKLE_DIR / "ANSUREIIPublic.pkl")
    # Define default attributes to display
    default_attributes = [
        "Sex",
        "Height [cm]",
        "Chest depth [cm]",
        "Bideltoid breadth [cm]",
    ]

    # Sidebar: allow users to select attributes dynamically
    st.sidebar.title("Adjust parameters")
    selected_attribute = st.sidebar.selectbox(
        "Select an attribute for distribution visualization:",
        options=default_attributes,
    )

    # Display title on the main page
    st.subheader("Visualisation")
    col1, col2 = st.columns([1.7, 1])  # Adjust proportions as needed
    with col1:
        fig = plot.display_distribution(df, selected_attribute.lower())
        st.plotly_chart(fig, use_container_width=True)
        # Sidebar: Button to download the graph in PDF format
        selected_attribute_name = selected_attribute.replace(" ", "_")
    with col2:
        # display the mean and standard deviation of the selected attribute for man and woman
        if selected_attribute != "Sex":
            df_male = df[df["sex"] == "male"]
            df_female = df[df["sex"] == "female"]
            st.write("**Male**")
            st.write(f"Mean = {df_male[selected_attribute].mean():.2f} cm ")
            st.write(f"Standard deviation = {df_male[selected_attribute].std():.2f} cm ")
            st.write("**Female**")
            st.write(f"Mean = {df_female[selected_attribute].mean():.2f} cm ")
            st.write(f"Standard deviation = {df_female[selected_attribute].std():.2f} cm ")

    # Download section in the sidebar
    st.sidebar.title("Download")
    st.sidebar.download_button(
        label="Download plot as PDF",
        data=fig.to_image(format="pdf"),
        file_name=f"{selected_attribute_name}_distribution.pdf",
        mime="application/pdf",
    )
    # Add a selectbox for choosing the dataset
    dataset_choice = st.sidebar.selectbox("Choose ANSUR II dataset to donwload:", ("Female", "Male"))
    # Define the filenames based on the choice
    path_file = Path(__file__).parent.parent.parent / "data" / "csv"
    filename_dict = {
        "Female": path_file / "ANSURIIFEMALEPublic.csv",
        "Male": path_file / "ANSURIIMALEPublic.csv",
    }
    df = fun.load_data(filename_dict[dataset_choice])

    # Create the download filename
    download_filename = f"anthropometric_data_{filename_dict[dataset_choice].stem}.csv"
    # Prepare the data for download
    data_to_download = df.to_csv(index=False).encode("utf-8")
    # Add the download button
    st.sidebar.download_button(
        label=f"Download {dataset_choice.lower()} dataset as CSV",
        data=data_to_download,
        file_name=download_filename,
        mime="text/csv",
    )


def run_tab_anthropometry() -> None:
    """Execute the main function for the anthropometry tab."""
    main()
