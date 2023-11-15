def write_yaml_file(data: Dict, filename: Text):
    """Writes a yaml file.

     Args:
        data: The data to write.
        filename: The path to the file which should be written.
    """
    with open(filename, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)