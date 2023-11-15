  def end(self):
    """This pants run is over, so stop tracking it.

    Note: If end() has been called once, subsequent calls are no-ops.

    :return: PANTS_SUCCEEDED_EXIT_CODE or PANTS_FAILED_EXIT_CODE
    """
    if self._end_memoized_result is not None:
      return self._end_memoized_result
    if self._background_worker_pool:
      if self._aborted:
        self.log(Report.INFO, "Aborting background workers.")
        self._background_worker_pool.abort()
      else:
        self.log(Report.INFO, "Waiting for background workers to finish.")
        self._background_worker_pool.shutdown()
      self.end_workunit(self._background_root_workunit)

    self.shutdown_worker_pool()

    # Run a dummy work unit to write out one last timestamp.
    with self.new_workunit("complete"):
      pass

    self.end_workunit(self._main_root_workunit)

    outcome = self._main_root_workunit.outcome()
    if self._background_root_workunit:
      outcome = min(outcome, self._background_root_workunit.outcome())
    outcome_str = WorkUnit.outcome_string(outcome)
    log_level = RunTracker._log_levels[outcome]
    self.log(log_level, outcome_str)

    if self.run_info.get_info('outcome') is None:
      # If the goal is clean-all then the run info dir no longer exists, so ignore that error.
      self.run_info.add_info('outcome', outcome_str, ignore_errors=True)

    if self._target_to_data:
      self.run_info.add_info('target_data', self._target_to_data)

    self.report.close()
    self.store_stats()

    run_failed = outcome in [WorkUnit.FAILURE, WorkUnit.ABORTED]
    result = PANTS_FAILED_EXIT_CODE if run_failed else PANTS_SUCCEEDED_EXIT_CODE
    self._end_memoized_result = result
    return self._end_memoized_result