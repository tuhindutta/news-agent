import os
import yaml
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()



def load_yaml_to_dict(filepath: str) -> dict | list | None:
    """
    Loads a YAML file and returns the content as a Python dictionary or list.

    Uses yaml.safe_load() to prevent arbitrary code execution from untrusted sources.

    Args:
        filepath: The path to the YAML file.

    Returns:
        The content of the YAML file as a Python dictionary, a list, or None if an error occurs.
    """
    try:
        with open(filepath, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return None
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")
        return None



class __Config(BaseModel):
    LAST_KEEP_MESSAGE_COUNT: int
    SUMMARIZE_MESSAGE_COUNT: int
    MCP_URI: str
    POSTGRES_CHECKPOINTER_URI: str

def process_config():
    config = load_yaml_to_dict("./config/config.yaml")
    for var in list(__Config.model_fields.keys()):
        config[var] = os.getenv(var, config.get(var))
    return config


Config = __Config(**process_config())