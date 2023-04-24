import os
import yaml


def load_config():
    with open(f"../config/config.yml", "r") as f:
        config = yaml.safe_load(f)
    return config
