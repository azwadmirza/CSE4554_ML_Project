    def process_results(self,
                        run_info: RunInfo,
                        incumbent: typing.Optional[Configuration],
                        run_history: RunHistory,
                        time_bound: float,
                        result: RunValue,
                        log_traj: bool = True,
                        ) -> \
            typing.Tuple[Configuration, float]:
        """
        The intensifier stage will be updated based on the results/status
        of a configuration execution.
        Also, a incumbent will be determined.

        Parameters
        ----------
        run_info : RunInfo
               A RunInfo containing the configuration that was evaluated
        incumbent : typing.Optional[Configuration]
            Best configuration seen so far
        run_history : RunHistory
            stores all runs we ran so far
            if False, an evaluated configuration will not be generated again
        time_bound : float
            time in [sec] available to perform intensify
        result: RunValue
            Contain the result (status and other methadata) of exercising
            a challenger/incumbent.
        log_traj: bool
            Whether to log changes of incumbents in trajectory

        Returns
        -------
        incumbent: Configuration
            current (maybe new) incumbent configuration
        inc_perf: float
            empirical performance of incumbent configuration
        """

        # Mark the fact that we processed this configuration
        self.run_tracker[(run_info.config, run_info.instance, run_info.seed, run_info.budget)] = True

        # If The incumbent is None and it is the first run, we use the challenger
        if not incumbent and self.first_run:
            self.logger.info(
                "First run, no incumbent provided; challenger is assumed to be the incumbent"
            )
            incumbent = run_info.config
            self.first_run = False

        # Account for running instances across configurations, not only on the
        # running configuration
        n_insts_remaining = self._get_pending_instances_for_stage(run_history)

        # Make sure that there is no Budget exhausted
        if result.status == StatusType.CAPPED:
            self.curr_inst_idx = np.inf
            n_insts_remaining = 0
        else:
            self._ta_time += result.time
            self.num_run += 1
            self.curr_inst_idx += 1

        # adding challengers to the list of evaluated challengers
        #  - Stop: CAPPED/CRASHED/TIMEOUT/MEMOUT/DONOTADVANCE (!= SUCCESS)
        #  - Advance to next stage: SUCCESS
        # curr_challengers is a set, so "at least 1" success can be counted by set addition (no duplicates)
        # If a configuration is successful, it is added to curr_challengers.
        # if it fails it is added to fail_challengers.
        if np.isfinite(self.curr_inst_idx) and result.status == StatusType.SUCCESS:
            self.success_challengers.add(run_info.config)  # successful configs
        elif np.isfinite(self.curr_inst_idx) and result.status == StatusType.DONOTADVANCE:
            self.do_not_advance_challengers.add(run_info.config)
        else:
            self.fail_challengers.add(run_info.config)  # capped/crashed/do not advance configs

        # We need to update the incumbent if this config we are processing
        # completes all scheduled instance-seed pairs.
        # Here, a config/seed/instance is going to be processed for the first time
        # (it has been previously scheduled by get_next_run and marked False, indicating
        # that it has not been processed yet. Entering process_results() this config/seed/instance
        # is marked as TRUE as an indication that it has finished and should be processed)
        # so if all configurations runs are marked as TRUE it means that this new config
        # was the missing piece to have everything needed to compare against the incumbent
        update_incumbent = all([v for k, v in self.run_tracker.items() if k[0] == run_info.config])

        # get incumbent if all instances have been evaluated
        if n_insts_remaining <= 0 or update_incumbent:
            incumbent = self._compare_configs(challenger=run_info.config,
                                              incumbent=incumbent,
                                              run_history=run_history,
                                              log_traj=log_traj)
        # if all configurations for the current stage have been evaluated, reset stage
        num_chal_evaluated = (
            len(self.success_challengers | self.fail_challengers | self.do_not_advance_challengers)
            + self.fail_chal_offset
        )
        if num_chal_evaluated == self.n_configs_in_stage[self.stage] and n_insts_remaining <= 0:

            self.logger.info('Successive Halving iteration-step: %d-%d with '
                             'budget [%.2f / %d] - evaluated %d challenger(s)' %
                             (self.sh_iters + 1, self.stage + 1, self.all_budgets[self.stage], self.max_budget,
                              self.n_configs_in_stage[self.stage]))

            self._update_stage(run_history=run_history)

        # get incumbent cost
        inc_perf = run_history.get_cost(incumbent)

        return incumbent, inc_perf