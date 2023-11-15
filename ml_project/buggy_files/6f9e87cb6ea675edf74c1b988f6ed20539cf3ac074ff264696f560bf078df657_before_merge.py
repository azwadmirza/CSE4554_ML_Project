  def _run(self):
    # Launch RunTracker as early as possible (just after Subsystem options are initialized).
    run_tracker = RunTracker.global_instance()
    reporting = Reporting.global_instance()
    reporting.initialize(run_tracker, self._options, self._run_start_time)

    try:
      # Capture a repro of the 'before' state for this build, if needed.
      repro = Reproducer.global_instance().create_repro()
      if repro:
        repro.capture(run_tracker.run_info.get_as_dict())

      engine_result = self._maybe_run_v2()
      goal_runner_result = self._maybe_run_v1(run_tracker, reporting)

      if repro:
        # TODO: Have Repro capture the 'after' state (as a diff) as well?
        repro.log_location_of_repro_file()
    finally:
      run_tracker_result = run_tracker.end()

    final_exit_code = self._compute_final_exit_code(
      engine_result,
      goal_runner_result,
      run_tracker_result
    )
    self._exiter.exit(final_exit_code)