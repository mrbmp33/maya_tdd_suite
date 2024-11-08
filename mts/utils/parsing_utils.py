import os
import re


# noinspection RegExpRedundantEscape
def resolve_env_variables_strings(dict_data):
    """Identifies custom syntax to pick up environment variables and performs their substitutions before returning raw
    yml data."""

    def replace_env_variable(match):
        env_variable = match.group(1)
        return os.environ.get(env_variable, "")

    # Replace placeholders with environment variable values
    processed_data = re.sub(r"\$ENV\{(\w+)\}", replace_env_variable, dict_data)

    return processed_data
