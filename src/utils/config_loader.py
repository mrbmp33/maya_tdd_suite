import pathlib
import os
import yaml
from utils import parsing_utils


def find_config() -> str:
    """Finds the configuration file relative to this project in case the env var hasn't been set yet."""

    # In case the package has not been initialized, this will make it fall back to building the variable
    os.environ.setdefault('MAYA_TDD_ROOT_DIR',
                          str(pathlib.Path(__file__).parent.parent.parent.resolve())
                          )
    # Default location
    config_file = pathlib.Path(os.environ['MAYA_TDD_ROOT_DIR']) / 'config' / 'config.yml'

    return str(config_file)


def load_config(config_file: str = None, resolve_vars=True) -> dict:
    """Loads a given yaml file for configuration. If none is passed it will automatically fall back to the environment
    variable <*TDD_CONFIG_FILE*> that holds the path to the package config file."""

    # Initialise env var if not already present before reading config file.
    config_file = config_file or pathlib.Path(os.getenv('TDD_CONFIG_FILE', find_config()))

    if not config_file.exists():
        raise EnvironmentError(f'Given config file <{config_file}> does not exist!')

    with open(str(config_file), "r") as f:
        if resolve_vars:
            config_content = parsing_utils.preprocess_yaml_with_env_variables(f.read())
        else:
            config_content = f.read()
        config = yaml.safe_load(config_content)
    return config


def write_to_config(new_values: dict, config_file: str = None):
    """Writes to the config file of choice.

    It will overwrite the difference between both dictionaries that make up the configuration.
    """

    config_file = config_file or pathlib.Path(os.getenv('TDD_CONFIG_FILE', find_config()))

    conf = load_config(config_file=config_file, resolve_vars=False)
    conf.update(new_values)

    with open(str(config_file), "w") as f:
        yaml.safe_dump(conf, f)


if __name__ == '__main__':
    from pprint import pprint
    pprint(load_config())
