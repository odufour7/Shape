"""Contains functions to convert crowd data to a ZIP file and save it."""

import io
import zipfile
from pathlib import Path

import configuration.backup.crowd_to_dict as to_dict
import configuration.backup.dict_to_xml_and_reverse as dict_to_xml
from configuration.models.crowd import Crowd


def write_crowd_data_to_zip(current_crowd: Crowd) -> io.BytesIO:
    """
    Generate a ZIP file containing XML representations of crowd parameters.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing the parameters to be saved.

    Returns
    -------
    io.BytesIO
        An in-memory ZIP file containing the XML representations of crowd parameters.
    """
    # Extract static pedestrian parameters and convert to XML
    static_data_dict = to_dict.get_static_params(current_crowd)
    static_data_bytes = dict_to_xml.static_dict_to_xml(static_data_dict)

    # Extract dynamic pedestrian parameters and convert to XML
    dynamic_data_dict = to_dict.get_dynamic_params(current_crowd)
    dynamic_data_bytes = dict_to_xml.dynamic_dict_to_xml(dynamic_data_dict)

    # Extract geometry parameters and convert to XML
    geometry_data_dict = to_dict.get_geometry_params(current_crowd)
    geometry_data_bytes = dict_to_xml.geometry_dict_to_xml(geometry_data_dict)

    # Extract material parameters and convert to XML
    materials_data_dict = to_dict.get_materials_params()
    materials_data_bytes = dict_to_xml.materials_dict_to_xml(materials_data_dict)

    # Create an in-memory ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Write each XML file into the ZIP archive
        zip_file.writestr("Agents.xml", static_data_bytes)
        zip_file.writestr("AgentDynamics.xml", dynamic_data_bytes)
        zip_file.writestr("Geometry.xml", geometry_data_bytes)
        zip_file.writestr("Materials.xml", materials_data_bytes)

    # Move the buffer's pointer to the beginning
    zip_buffer.seek(0)
    return zip_buffer


def save_crowd_data_to_zip(current_crowd: Crowd, output_zip_path: Path) -> None:
    """
    Save crowd data as a ZIP file containing multiple XML files.

    Parameters
    ----------
    current_crowd : Crowd
        The current crowd object containing the parameters to be saved.
    output_zip_path : Path
        The path where the ZIP file will be saved.

    Raises
    ------
    TypeError
        If `output_zip_path` is not a Path object.
    ValueError
        If `output_zip_path` does not have a .zip extension.
    """
    if not isinstance(output_zip_path, Path):
        raise TypeError("`output_zip_path` should be a Path object.")
    if not output_zip_path.suffix == ".zip":
        raise ValueError("`output_zip_path` should have a .zip extension.")

    # Ensure the output directory exists
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate the ZIP file in memory
    zip_buffer = write_crowd_data_to_zip(current_crowd)

    # Write the in-memory ZIP file to the specified output path
    with open(output_zip_path, "wb") as output_file:
        output_file.write(zip_buffer.read())

    # Close the in-memory buffer
    zip_buffer.close()
