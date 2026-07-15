import argparse
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Any


class HubData(BaseModel):
    """Validates raw hub data extracted from the map file.

    Attributes:
        name (str): The unique identifier of the hub.
        x (int): The X coordinate.
        y (int): The Y coordinate.
    """
    name: str
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    color: Optional[str] = None
    zone: str = Field(default="normal")
    max_drones: int = Field(ge=1, default=1)


class LinkData(BaseModel):
    """Validates raw connection data extracted from the map file.

    Attributes:
        hub_a (str): The name of the first connected hub.
        hub_b (str): The name of the second connected hub.
        max_link_capacity (int): Maximum drones allowed
        on the link simultaneously.
    """
    hub_a: str
    hub_b: str
    max_link_capacity: int = Field(ge=1, default=1)


def valid_txt_file(filepath: str) -> str:
    """Validates that the provided filepath has a .txt extension.

    Args:
        filepath (str): The path to check.

    Returns:
        str: The validated filepath.

    Raises:
        argparse.ArgumentTypeError: If the extension is not .txt.
    """
    if not filepath.lower().endswith('.txt'):
        raise argparse.ArgumentTypeError(
            f"The file '{filepath}' must be a .txt file."
        )
    return filepath


def parse_arguments() -> str:
    """Parses command-line arguments to get the map file path.

    Returns:
        str: The path to the simulation map file.
    """
    parser = argparse.ArgumentParser(description="Fly-in drone routing.")
    parser.add_argument(
        "map_file",
        type=valid_txt_file,
        help="Path to the .txt map file to parse."
    )
    args: argparse.Namespace = parser.parse_args()
    return args.map_file


def parse_metadata(metadata_str: str) -> dict[str, str]:
    """Parses the optional metadata string into a dictionary.

    Args:
        metadata_str (str): The metadata string enclosed in brackets,
            e.g., "[zone=restricted color=red]".

    Returns:
        dict[str, str]: A dictionary of metadata key-value pairs.
    """
    clean_meta: str = metadata_str.strip("[]")
    if not clean_meta:
        return {}
    meta_list: list[str] = clean_meta.split(" ")
    meta_dict: dict[str, str] = {
        m.split("=")[0]: m.split("=")[1]
        for m in meta_list if "=" in m
    }
    return meta_dict


def parse_map_file(filepath: str) -> dict[str, Any]:
    """Parses the input simulation file and builds the network graph.

    Reads the file line by line, extracting the number of drones,
    hubs data and connection data.
    Ignores comments starting with '#'.

    Args:
        filepath (str): The path to the input map file.

    Raises:
        ValueError: If a parsing error occurs or a zone type is invalid.

    Return:
        A list of dictionnaries containing the differents data type.
    """
    config: dict[str, Any] = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line: str = line.strip()
            if not clean_line or clean_line.startswith('#'):
                continue
            data = clean_line.split(":")
            if data[0] == "start_hub":
                start_data = data[1].split()
                config["start_hub"] = {"name": start_data[0], "x": start_data[1], "y": start_data[2]}
                if start_data[3]:
                    optional = parse_metadata(start_data[3])
                    config["start_hub"].update(optional)
            if data[0] == "end_hub":
                end_data = data[1].split()
                config["end_hub"] = {"name": end_data[0], "x": end_data[1], "y": end_data[2]}
                if end_data[3]:
                    optional = parse_metadata(end_data[3])
                    config["end_hub"].update(optional)
            if data[0] == "hub":
                if data[0] not in config:
                    hub: list[dict[str, str]] = []
                    config["hub"] = hub
                    
