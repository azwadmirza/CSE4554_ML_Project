  def __init__(self, build_root, exiter, options, options_bootstrapper, build_config, target_roots,
               graph_session, is_daemon, profile_path):
    """
    :param string build_root: The build root for this run.
    :param Exiter exiter: The Exiter instance to use for this run.
    :param Options options: The parsed options for this run.
    :param OptionsBootstrapper options_bootstrapper: The OptionsBootstrapper instance to use.
    :param BuildConfiguration build_config: The parsed build configuration for this run.
    :param TargetRoots target_roots: The `TargetRoots` for this run.
    :param LegacyGraphSession graph_session: A LegacyGraphSession instance for graph reuse.
    :param bool is_daemon: Whether or not this run was launched with a daemon graph helper.
    :param string profile_path: The profile path - if any (from from the `PANTS_PROFILE` env var).
    """
    self._build_root = build_root
    self._exiter = exiter
    self._options = options
    self._options_bootstrapper = options_bootstrapper
    self._build_config = build_config
    self._target_roots = target_roots
    self._graph_session = graph_session
    self._is_daemon = is_daemon
    self._profile_path = profile_path

    self._run_start_time = None
    self._global_options = options.for_global_scope()