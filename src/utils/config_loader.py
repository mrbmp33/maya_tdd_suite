from typing import Optional
import os
import yaml


def load_config(config_file: Optional[str] = None) -> dict:
    """Loads a given yaml file for configuration. If none is passed it will automatically fall back to the environment
    variable <*TDD_CONFIG_FILE*> that holds the path to the package config file."""
    
    config_file = config_file or os.getenv('TDD_CONFIG_FILE')
    
    if config_file is None:
        raise ValueError('Could not find any configuration file. Check the TDD_CONFIG_FILE environment variable.')
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config
