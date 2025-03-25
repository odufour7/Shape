import shutil
import zipfile
from pathlib import Path
from typing import List, Union

import requests
import streamlit as st


def download(url: str, destination: Union[str, Path]) -> None:
    """Download a file from a specified URL and saves it to a given destination."""
    # Send a GET request
    response = requests.get(url, stream=True)

    # Total size in bytes.
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kbyte
    progress_bar = st.progress(0)
    progress_status = st.empty()
    written = 0

    with open(destination, "wb") as f:
        for data in response.iter_content(block_size):
            written += len(data)
            f.write(data)
            # Update progress bar
            progress = int(100 * written / total_size)
            progress_bar.progress(progress)
            progress_status.text(f"> {progress}%")

    progress_status.text("Download complete.")
    progress_bar.empty()  # clear  the progress bar after completion


######## sets up a basic logging configuration for a Python application #####
import logging


def setup_logging() -> None:
    """Define logging setup."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


#######   Download and unzip files from a zenodo url  ######


@dataclass
class DataConfig:
    """Datastructure for the app."""

    trajectories_directory: Path
    flow_directory: Path
    # results
    processed_directory: Path
    files: List[str] = field(default_factory=list)
    url: str = "https://go.fzj.de/madras-data"

    def __post_init__(self) -> None:
        """Initialize the DataConfig instance by retrieving files for each country."""
        # self.data.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Create {self.processed_directory}")
        self.processed_directory.mkdir(parents=True, exist_ok=True)
        self.retrieve_files()

    def retrieve_files(self) -> None:
        """Retrieve the files for each country specified in the countries list."""
        logging.info("Retrieve data ...")
        if not self.trajectories_directory.exists():
            st.warning(f"{self.trajectories_directory} does not exist yet!")
            with st.status("Downloading ...", expanded=False):
                download_and_unzip_files(self.url, "data.zip", self.trajectories_directory)

        else:
            logging.info("Found trajectory directory. Nothing to retrieve!")
        self.files = sorted(glob.glob(f"{self.trajectories_directory}/*.txt"))


def unzip_files(zip_path: Union[str, Path], destination: Union[str, Path]) -> None:
    """
    Unzip a ZIP file directly into the specified destination directory.

    Ignoring the original directory structure in the ZIP file.

    Parameters:
    - zip_path (str): The path to the ZIP file.
    - destination (str): The directory where files should be extracted.
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.infolist():
            st.info(f"member: {member}")
            # Extract only if file (ignores directories)
            if not member.is_dir():
                # Build target filename path
                target_path = os.path.join(destination, os.path.basename(member.filename))
                st.info(f"targe_path {target_path}")
                # Ensure target directory exists (e.g., if not extracting directories)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                # Extract file
                with (
                    zip_ref.open(member, "r") as source,
                    open(target_path, "wb") as target,
                ):
                    shutil.copyfileobj(source, target)


def download_and_unzip_files(url: str, destination: Union[str, Path], unzip_destination: Union[str, Path]) -> None:
    """
    Download a ZIP file from a specified URL.

    Saves it to a given destination, and unzips it into a specified directory.
    Displays the download and unzipping progress in a Streamlit app.
    """
    # Send a GET request
    response = requests.get(url, stream=True)

    # Total size in bytes.
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kbyte
    progress_bar = st.progress(0)
    progress_status = st.empty()
    written = 0

    with open(destination, "wb") as f:
        for data in response.iter_content(block_size):
            written += len(data)
            f.write(data)
            # Update progress bar
            progress = int(100 * written / total_size)
            progress_bar.progress(progress)
            progress_status.text(f"> {progress}%")

    progress_status.text("Download complete. Unzipping...")
    unzip_files(destination, unzip_destination)

    progress_status.text("Unzipping complete.")
    progress_bar.empty()  # Clear the progress bar after completion
