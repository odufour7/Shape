"""Export agent trajectories from XML files to CHAOS format."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pandas as pd

regex_nb = r"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?"


def get_list_of_agents_and_times_from_XML(
    folder_path: Path,
) -> tuple[list[str], list[float], dict[int, str]]:
    """
    Extract a sorted list of unique agent IDs, sorted list of times, and a dictionary of filenames from XML files in a folder.

    Parameters
    ----------
    folder_path : Path
        Path to the folder containing XML files.

    Returns
    -------
    list[str]
        Sorted list of unique agent IDs found in the XML files.
    list[float]
        Sorted list of times extracted from the filenames.
    dict[int, str]
        Dictionary mapping time (as int, scaled by 1000) to the corresponding filename.

    Notes
    -----
    Assumes XML files are named with the pattern 'AgentDyn...output t=<time>.xml'.
    """
    ID_agents: set[str] = set()
    times: list[float] = []
    filenames: dict[int, str] = {}

    for fichier in folder_path.iterdir():
        if fichier.is_file() and fichier.name.startswith("AgentDyn") and fichier.name.endswith("xml"):
            m = re.fullmatch(r".*output t=(" + regex_nb + r").xml", str(fichier))
            if not m:
                continue
            time_loc = float(m.group(1))
            times.append(time_loc)
            filenames[int(1000 * time_loc)] = str(fichier)

            agents_tree = ET.parse(fichier).getroot()
            for agent in agents_tree:
                agent_id = agent.get("Id")
                if agent_id is not None:
                    ID_agents.add(agent_id)
            del agents_tree

    return sorted(ID_agents), sorted(times), filenames


def create_dict_of_agent_trajectories(
    folder_path: Path,
) -> tuple[list[float], dict[str, dict[float, dict[str, float]]]]:
    """
    Create a dictionary of agent trajectories from XML files in a folder.

    For each agent, stores their position and velocity at each time point.

    Parameters
    ----------
    folder_path : Path
        Path to the folder containing XML files.

    Returns
    -------
    list[float]
        Sorted list of all time points extracted from the XML filenames.
    dict[str, dict[float, dict[str, float]]]
        Nested dictionary such that:
        agents[agent_id][time] = {
            'x': pos_x,
            'y': pos_y,
            'vx': vel_x,
            'vy': vel_y
        }.

    Notes
    -----
    Assumes XML files are named and structured as expected by `get_list_of_agents_and_times_from_XML`.
    """
    ID_agents, times, filenames = get_list_of_agents_and_times_from_XML(folder_path)

    agents: dict[str, dict[float, dict[str, float]]] = {ID: {} for ID in ID_agents}

    for time_loc in times:
        file_path = filenames[int(1000 * time_loc)]
        agents_tree = ET.parse(file_path).getroot()

        for agent in agents_tree:
            ID_agent = agent.get("Id")
            if ID_agent is None:
                continue

            kinematics = next(agent.iterfind("Kinematics"), None)
            if kinematics is None:
                continue

            pos = kinematics.get("Position")
            vel = kinematics.get("Velocity")
            if pos is None or vel is None:
                continue

            pos_match = re.fullmatch(rf"({regex_nb}),({regex_nb})", pos)
            vel_match = re.fullmatch(rf"({regex_nb}),({regex_nb})", vel)
            if not pos_match or not vel_match:
                continue

            agents[ID_agent][time_loc] = {
                "x": float(pos_match.group(1)),
                "y": float(pos_match.group(2)),
                "vx": float(vel_match.group(1)),
                "vy": float(vel_match.group(2)),
            }

        del agents_tree

    return times, agents


def export_dict_to_CSV(folder_path: Path, filename_CSV: str) -> None:
    """
    Export agent trajectories to a CSV file with header: t,ID,x,y,vx,vy.

    Each row of the CSV contains the time, agent ID, position (x, y), and velocity (vx, vy) for each agent at each time point.

    Parameters
    ----------
    folder_path : Path
        Path to the folder containing the XML files.
    filename_CSV : str
        Name of the output CSV file to create within the folder.
    """
    times, agents = create_dict_of_agent_trajectories(folder_path)
    ID_agents = sorted(agents.keys())
    csv_path = folder_path / filename_CSV

    with open(csv_path, "w", encoding="utf-8") as monfichier:
        monfichier.write("t,ID,x,y,vx,vy")
        for time_loc in times:
            for ID_agent in ID_agents:
                posvel = agents[ID_agent].get(time_loc)
                if posvel is not None:
                    monfichier.write(
                        f"\n{time_loc:.4f},{ID_agent},{posvel['x']:.6f},{posvel['y']:.6f},{posvel['vx']:.6f},{posvel['vy']:.6f}"
                    )


def export_from_CSV_to_CHAOS(path_to_CSV: Path, folder_CHAOS: Path, dt: float) -> None:
    """
    Read agent trajectories from a CSV file and exports them into multiple text files in the format required by the CHAOS software.

    For each unique agent ID, creates a file containing interpolated positions at regular time steps.

    Parameters
    ----------
    path_to_CSV : Path
        Path to the input CSV file containing columns: t, ID, x, y, vx, vy.
    folder_CHAOS : Path
        Path to the output folder where CHAOS trajectory files will be saved.
    dt : float
        Timestep to use for interpolation in the CHAOS output.

    Notes
    -----
    Each output file is named 'trajXXX.csv' where XXX is the zero-padded agent index.
    Each line in the output file contains: t, x, y, 0.0
    """
    folder_CHAOS.mkdir(parents=True, exist_ok=True)
    if not path_to_CSV.is_file() or path_to_CSV.suffix != ".csv":
        raise ValueError(f"Path {path_to_CSV} is not a valid CSV file.")

    lignes = pd.read_csv(path_to_CSV, sep=",", header=0, index_col=False)
    lignes["t"] = lignes["t"].astype(float)
    lignes.sort_values(by=["ID", "t"], inplace=True)

    t_min = lignes["t"].min()
    t_max = lignes["t"].max()
    t_vec = np.arange(t_min, t_max, dt)

    for cpt_agent, ID in enumerate(sorted(lignes["ID"].unique())):
        lignes_loc = lignes[lignes["ID"] == ID].reset_index(drop=True)
        times = lignes_loc["t"].values
        xs = lignes_loc["x"].values
        ys = lignes_loc["y"].values

        out_path = folder_CHAOS / f"traj{cpt_agent:03d}.csv"
        with open(out_path, "w", encoding="utf-8") as monfichier:
            for t in t_vec:
                # Find indices before and after t
                idx_after = np.searchsorted(times, t, side="right")
                if idx_after == 0 or idx_after == len(times):
                    # If t is outside the trajectory time range, skip
                    continue
                idx_before = idx_after - 1

                t_before = times[idx_before]
                t_after = times[idx_after]
                x_before = xs[idx_before]
                x_after = xs[idx_after]
                y_before = ys[idx_before]
                y_after = ys[idx_after]

                # Linear interpolation
                coef = (t - t_before) / (t_after - t_before)
                x_interp = (1.0 - coef) * x_before + coef * x_after
                y_interp = (1.0 - coef) * y_before + coef * y_after

                monfichier.write(f"{t:.3f},{x_interp:.3f},{y_interp:.3f},0.0\n")

    print("* Trajectories have been converted to Chaos-compatible files")
