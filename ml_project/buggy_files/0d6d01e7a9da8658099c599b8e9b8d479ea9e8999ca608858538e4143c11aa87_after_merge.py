  def _setup_pailgun(self):
    """Sets up a PailgunServer instance."""
    # Constructs and returns a runnable PantsRunner.
    def runner_factory(sock, arguments, environment):
      exiter = self._exiter_class(sock)
      build_graph = None

      self._logger.debug('execution commandline: %s', arguments)
      if self._scheduler_service:
        # N.B. This parses sys.argv by way of OptionsInitializer/OptionsBootstrapper prior to
        # the main pants run to derive spec_roots for caching in the underlying scheduler.
        spec_roots = self._parse_commandline_to_spec_roots(args=arguments)
        self._logger.debug('parsed spec_roots: %s', spec_roots)
        try:
          self._logger.debug('requesting BuildGraph from %s', self._scheduler_service)
          # N.B. This call is made in the pre-fork daemon context for reach and reuse of the
          # resident scheduler for BuildGraph construction.
          build_graph = self._scheduler_service.get_build_graph(spec_roots)
        except Exception:
          self._logger.warning(
            'encountered exception during SchedulerService.get_build_graph():\n%s',
            traceback.format_exc()
          )
      return self._runner_class(sock, exiter, arguments, environment, build_graph)

    @contextmanager
    def context_lock():
      """This lock is used to safeguard Pailgun request handling against a fork() with the
      scheduler lock held by another thread (e.g. the FSEventService thread), which can
      lead to a pailgun deadlock.
      """
      if self._scheduler_service:
        with self._scheduler_service.locked():
          yield
      else:
        yield

    return PailgunServer(self._bind_addr, runner_factory, context_lock)