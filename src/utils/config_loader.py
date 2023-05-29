import pathlib
import os
import yaml


def load_config() -> dict:
    """Loads a given yaml file for configuration. If none is passed it will automatically fall back to the environment
    variable <*TDD_CONFIG_FILE*> that holds the path to the package config file."""
    
    config_file = pathlib.Path(
        os.getenv(
            'MAYA_TDD_ROOT_DIR',
            str(pathlib.Path(__file__).parent.parent.resolve())
        )) / 'config' / 'config.yml'
    
    if config_file is None:
        raise EnvironmentError('Could not find any configuration file. Check the TDD_CONFIG_FILE environment variable.')
    
    with open(str(config_file), "r") as f:
        config = yaml.safe_load(f)
    return config
