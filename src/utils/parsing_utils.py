import yaml

def flatten_dict(nested_dict, parent_key='', separator='.'):
    flattened_dict = {}
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, separator))
        else:
            flattened_dict[new_key] = value
    return flattened_dict


# noinspection RegExpRedundantEscape
def preprocess_yaml_with_env_variables(yaml_content):

    data = yaml.safe_load(yaml_content)
    keys =

    def replace_env_variable(match):
        env_variable = match.group(1)
        return os.environ.get(env_variable, "")

    # def replace_self_reference(match):
    #     key = match.group(1)
    #     return str(data[key]) if key in yaml_content else match.group(0)

    # Replace placeholders with environment variable values
    processed_yaml = re.sub(r"\$ENV\{(\w+)\}", replace_env_variable, yaml_content)
    # processed_yaml = re.sub(r"\$\{(\w+)\}", replace_self_reference, processed_yaml)

    return processed_yaml
