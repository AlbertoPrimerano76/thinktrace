import os
import yaml
from typing import Optional
from core import logger,config_manager


def load_simulation_prompt(path: Optional[str] = None) -> str:
    """
    Load and return the simulation prompt template from a YAML file.
    
    Args:
        path (str): The path to the YAML file containing the prompt template.
    
    Returns:
        str: The simulation prompt template as a string.
    
    Raises:
        FileNotFoundError: If the YAML file does not exist.
        ValueError: If the YAML file is malformed or does not contain a 'template' field.
    """
    if path is None:
        path = config_manager.CONFIG_FOLDER_PATH +"/"+config_manager.PROMPT_FILE_NAME
    
    if not os.path.exists(path):
        logger.error(f"Prompt file not found at path: {path}")
        raise FileNotFoundError(f"Prompt file not found: {path}")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            prompt_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.exception(f"Failed to parse YAML from prompt file: {path}")
        raise ValueError(f"Invalid YAML format in prompt file: {path}") from e

    if not prompt_data or "template" not in prompt_data:
        logger.error(f"No 'template' key found in the prompt file: {path}")
        raise ValueError(f"Missing 'template' field in prompt YAML: {path}")
    
    logger.debug(f"Successfully loaded simulation prompt from: {path}")
    return prompt_data["template"]
