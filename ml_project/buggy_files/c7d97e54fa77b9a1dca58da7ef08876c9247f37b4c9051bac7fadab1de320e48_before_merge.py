  def _maybe_run_v2(self):
    # N.B. For daemon runs, @console_rules are invoked pre-fork -
    # so this path only serves the non-daemon run mode.
    if self._is_daemon or not self._global_options.v2:
      return 0

    # If we're a pure --v2 run, validate goals - otherwise some goals specified
    # may be provided by the --v1 task paths.
    if not self._global_options.v1:
      self._graph_session.validate_goals(self._options.goals_and_possible_v2_goals)

    try:
      self._graph_session.run_console_rules(
        self._options_bootstrapper,
        self._options.goals_and_possible_v2_goals,
        self._target_roots,
      )
    except GracefulTerminationException as e:
      logger.debug('Encountered graceful termination exception {}; exiting'.format(e))
      return e.exit_code
    except Exception as e:
      logger.warn('Encountered unhandled exception {} during rule execution!'
                  .format(e))
      return 1
    else:
      return 0