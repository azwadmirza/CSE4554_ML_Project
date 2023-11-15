    def maybe_launch(cls, options_bootstrapper):
      """Creates and launches a daemon instance if one does not already exist.

      :param OptionsBootstrapper options_bootstrapper: The bootstrap options.
      :returns: A Handle for the running pantsd instance.
      :rtype: PantsDaemon.Handle
      """
      stub_pantsd = cls.create(options_bootstrapper, full_init=False)
      with stub_pantsd._services.lifecycle_lock:
        if stub_pantsd.needs_restart(stub_pantsd.options_fingerprint):
          # Once we determine we actually need to launch, recreate with full initialization.
          pantsd = cls.create(options_bootstrapper)
          return pantsd.launch()
        else:
          # We're already launched.
          return PantsDaemon.Handle(
              stub_pantsd.await_pid(10),
              stub_pantsd.read_named_socket('pailgun', int),
              text_type(stub_pantsd._metadata_base_dir),
          )