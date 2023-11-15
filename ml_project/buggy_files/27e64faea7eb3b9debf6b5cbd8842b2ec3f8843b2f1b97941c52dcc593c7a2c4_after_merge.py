def TestInit():
  """Only used in tests and will rerun all the hooks to create a clean state."""
  # Tests use both the server template grr_server.yaml as a primary config file
  # (this file does not contain all required options, e.g. private keys), and
  # additional configuration in test_data/grr_test.yaml which contains typical
  # values for a complete installation.
  if stats.STATS is None:
    stats.STATS = stats.StatsCollector()

  flags.FLAGS.config = config_lib.Resource().Filter(
      "install_data/etc/grr-server.yaml")

  flags.FLAGS.secondary_configs = [config_lib.Resource().Filter(
      "test_data/grr_test.yaml@grr-response-test")]

  # We are running a test so let the config system know that.
  config_lib.CONFIG.AddContext(
      "Test Context", "Context applied when we run tests.")

  AddConfigContext()
  ConfigInit()

  # Tests additionally add a test configuration file.
  ServerLoggingStartupInit()
  registry.TestInit()