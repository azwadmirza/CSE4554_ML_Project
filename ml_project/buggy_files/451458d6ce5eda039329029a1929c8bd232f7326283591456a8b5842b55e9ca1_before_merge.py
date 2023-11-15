    def choose_trial_to_run(self, trial_runner):
        """Fair scheduling within iteration by completion percentage.

        List of trials not used since all trials are tracked as state
        of scheduler. If iteration is occupied (ie, no trials to run),
        then look into next iteration.
        """

        for hyperband in self._hyperbands:
            # band will have None entries if no resources
            # are to be allocated to that bracket.
            scrubbed = [b for b in hyperband if b is not None]
            for bracket in scrubbed:
                for trial in bracket.current_trials():
                    if (trial.status == Trial.PENDING
                            and trial_runner.has_resources(trial.resources)):
                        return trial
        # MAIN CHANGE HERE!
        if not any(t.status == Trial.RUNNING
                   for t in trial_runner.get_trials()):
            for hyperband in self._hyperbands:
                for bracket in hyperband:
                    if bracket and any(trial.status == Trial.PAUSED
                                       for trial in bracket.current_trials()):
                        # This will change the trial state and let the
                        # trial runner retry.
                        self._process_bracket(trial_runner, bracket)
        # MAIN CHANGE HERE!
        return None