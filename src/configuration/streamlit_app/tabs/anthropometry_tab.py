"""Visualise the anthropometric ANSURII dataset."""

from pathlib import Path

import streamlit as st

from configuration.streamlit_app.plot import plot
from configuration.utils import loading_backup_functions as lb_fun


def run_tab_anthropometry() -> None:
    """
    Provide an interactive interface for visualizing and analyzing anthropometric data from the ANSUR II database.

    Attributes
    ----------
    Sidebar:
        - Attribute selection for distribution visualization.
        - Download options for plots (PDF) and datasets (CSV).
        - Dataset selection (Male or Female).
    Main Page:
        - Visualization of the selected attribute's distribution using Plotly.
        - Statistical summaries (mean and standard deviation) for males and females.
        - Link to the ANSUR II database website.
    """
    # Load the dataset from a pickle file
    path_file = Path(__file__).parent.parent.parent.parent.parent / "data" / "pkl"
    df = lb_fun.load_pickle(path_file / "ANSUREIIPublic.pkl")

    # Define default attributes to display
    default_attributes = [
        "Sex",
        "Height [cm]",
        "Chest depth [cm]",
        "Bideltoid breadth [cm]",
        "Weight [kg]",
    ]

    # Sidebar: allow users to select attributes dynamically
    st.sidebar.title("Adjust parameters")
    selected_attribute = st.sidebar.selectbox(
        "Select an attribute for distribution visualization:",
        options=default_attributes,
    )

    # Display title on the main page
    st.subheader("Visualisation of the ANSURII database")
    # Define the URL of the database website
    database_url = "https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx"
    # Use st.markdown to create a clickable link
    st.markdown(f"Visit the [database website]({database_url})")

    # Main page content
    col1, col2 = st.columns([1.7, 1])  # Adjust proportions as needed
    with col1:
        fig = plot.display_distribution(df, selected_attribute.lower())
        st.plotly_chart(fig, use_container_width=True)
        # Sidebar: Button to download the graph in PDF format
        selected_attribute_name = selected_attribute.replace(" ", "_")
    with col2:
        # display the mean and standard deviation of the selected attribute for man and woman
        if selected_attribute.lower() not in ["sex", "weight [kg]"]:
            df_male = df[df["sex"] == "male"]
            df_female = df[df["sex"] == "female"]
            st.write("**Male**")
            st.write(f"Mean = {df_male[selected_attribute.lower()].mean():.2f} cm ")
            st.write(f"Standard deviation = {df_male[selected_attribute.lower()].std():.2f} cm ")
            st.write("**Female**")
            st.write(f"Mean = {df_female[selected_attribute.lower()].mean():.2f} cm ")
            st.write(f"Standard deviation = {df_female[selected_attribute.lower()].std():.2f} cm ")
        elif selected_attribute.lower() == "weight [kg]":
            df_male = df[df["sex"] == "male"]
            df_female = df[df["sex"] == "female"]
            st.write("**Male**")
            st.write(f"Mean = {df_male[selected_attribute.lower()].mean():.2f} kg ")
            st.write(f"Standard deviation = {df_male[selected_attribute.lower()].std():.2f} kg ")
            st.write("**Female**")
            st.write(f"Mean = {df_female[selected_attribute.lower()].mean():.2f} kg ")
            st.write(f"Standard deviation = {df_female[selected_attribute.lower()].std():.2f} kg ")

    # Download section in the sidebar
    st.sidebar.title("Download")

    # Add a download button for the plot
    st.sidebar.download_button(
        label="Download plot as PDF",
        data=fig.to_image(format="pdf"),
        file_name=f"{selected_attribute_name}_distribution.pdf",
        mime="application/pdf",
    )

    # Add a selectbox for choosing the dataset to download
    dataset_choice = st.sidebar.selectbox("Choose ANSUR II dataset to download:", ("Female", "Male"))
    path_file = Path(__file__).parent.parent.parent.parent.parent / "data" / "csv"
    filename_dict = {
        "Female": path_file / "ANSURIIFEMALEPublic.csv",
        "Male": path_file / "ANSURIIMALEPublic.csv",
    }
    df = lb_fun.load_csv(filename_dict[dataset_choice])
    download_filename = f"anthropometric_data_{filename_dict[dataset_choice].stem}.csv"
    # Prepare the data for download
    data_to_download = df.to_csv(index=False).encode("utf-8")
    # Add the download button for the dataset
    st.sidebar.download_button(
        label=f"Download {dataset_choice.lower()} dataset as CSV",
        data=data_to_download,
        file_name=download_filename,
        mime="text/csv",
    )
