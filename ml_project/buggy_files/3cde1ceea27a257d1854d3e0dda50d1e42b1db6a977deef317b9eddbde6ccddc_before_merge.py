  def _maybe_run_v1(self, run_tracker, reporting):
    if not self._global_options.v1:
      return 0

    # Setup and run GoalRunner.
    goal_runner_factory = GoalRunner.Factory(
      self._build_root,
      self._options,
      self._build_config,
      run_tracker,
      reporting,
      self._graph_session,
      self._target_roots,
      self._exiter
    )
    return goal_runner_factory.create().run()