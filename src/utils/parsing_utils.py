import os
import re
import yaml


# noinspection RegExpRedundantEscape
def preprocess_yaml_with_env_variables(yaml_content):
    """Identifies custom syntax to pick up environment variables and performs their substitutions before returning raw
    yml data."""

    data = yaml.safe_load(yaml_content)

    def replace_env_variable(match):
        env_variable = match.group(1)
        return os.environ.get(env_variable, "")

    # Replace placeholders with environment variable values
    processed_yaml = re.sub(r"\$ENV\{(\w+)\}", replace_env_variable, yaml_content)

    return processed_yaml
