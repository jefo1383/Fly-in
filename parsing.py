import argparse
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Any
import sys


class HubData(BaseModel):
    """Validates raw hub data extracted from the map file.

    Attributes:
        name (str): The unique identifier of the hub.
        x (int): The X coordinate.
        y (int): The Y coordinate.
        color (str): The optional hub color
    """
    name: str
    x: int
    y: int
    zone: str = Field(default="normal")
    color: Optional[str] = Field(default=None)
    max_drones: int = Field(ge=1, default=1)


class LinkData(BaseModel):
    """Validates raw connection data extracted from the map file.

    Attributes:
        hub_1 (str): The name of the first connected hub.
        hub_2 (str): The name of the second connected hub.
        max_link_capacity (int): Maximum drones allowed
        on the link simultaneously.
    """
    hub_1: str
    hub_2: str
    max_link_capacity: int = Field(ge=1, default=1)


def _valid_txt_file(filepath: str) -> str:
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
        type=_valid_txt_file,
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
    """Parses the input simulation file.

    Reads the file line by line, extracting the number of drones,
    hubs data and connection data.
    Ignores comments starting with '#'.

    Args:
        filepath (str): The path to the input map file.

    Raises:
        ValueError: If a parsing error occurs.
        ValidationError: If a type or name doesn't match pydantic's.

    Return:
        A dictionnarie containing the differents data type.
    """
    config: dict[str, Any] = {
        "nb_drones": 0,
        "start_hub": None,
        "end_hub": None,
        "hubs": [],
        "connections": []
    }
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                clean_line: str = line.strip()
                if not clean_line or clean_line.startswith('#'):
                    continue

                data = clean_line.split(":", 1)
                if len(data) != 2:
                    continue
                prefix: str = data[0].strip()
                content: str = data[1].strip()

                base_str: str = content
                meta_str: str = ""
                if "[" in content:
                    base_str, meta_str = content.split("[", 1)
                    meta_str = "[" + meta_str

                base_data: list[str] = base_str.split()

                if (prefix == "start_hub" or prefix == "end_hub"
                        or prefix == "hub"):
                    hub_dict: dict[str, Any] = {
                        "name": base_data[0],
                        "x": int(base_data[1]),
                        "y": int(base_data[2])
                    }
                    if meta_str:
                        hub_dict.update(parse_metadata(meta_str))

                    validated_hub = HubData(**hub_dict)

                    if prefix == "hub":
                        config["hubs"].append(validated_hub)
                    else:
                        config[prefix] = validated_hub

                if prefix == "connection":
                    base_data = [name.strip() for name in base_str.split("-")]
                    link_dict: dict[str, Any] = {
                        "hub_1": base_data[0],
                        "hub_2": base_data[1]
                    }
                    if meta_str:
                        link_dict.update(parse_metadata(meta_str))

                    validated_link = LinkData(**link_dict)

                    config["connections"].append(validated_link)

                if prefix == "nb_drones":
                    config["nb_drones"] = int(content)
    except (ValidationError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    return config
