  def _run(self):
    try:
      engine_result = self._maybe_run_v2()
      goal_runner_result = self._maybe_run_v1()
    finally:
      try:
        run_tracker_result = self._run_tracker.end()
      except ValueError as e:
        # Calling .end() sometimes writes to a closed file, so we return a dummy result here.
        logger.exception(e)
        run_tracker_result = PANTS_SUCCEEDED_EXIT_CODE

    final_exit_code = self._compute_final_exit_code(
      engine_result,
      goal_runner_result,
      run_tracker_result
    )
    self._exiter.exit(final_exit_code)