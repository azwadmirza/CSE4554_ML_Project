def load_config(config_paths, config=None):
  """Loads configuration files.

  Args:
    config_paths: A list of configuration files.
    config: A (possibly non empty) config dictionary to fill.

  Returns:
    The configuration dictionary.
  """
  if config is None:
    config = {}

  for config_path in config_paths:
    with open(config_path) as config_file:
      subconfig = yaml.load(config_file.read())

      # Add or update section in main configuration.
      for section in subconfig:
        if section in config:
          config[section].update(subconfig[section])
        else:
          config[section] = subconfig[section]

  return config