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

        # If The incumbent is None and it is the first run, we use the challenger
        if not incumbent and self.first_run:
            self.logger.info(
                "First run, no incumbent provided; challenger is assumed to be the incumbent"
            )
            incumbent = run_info.config
            self.first_run = False

        # selecting instance-seed subset for this budget, depending on the kind of budget
        curr_budget = self.all_budgets[self.stage]
        if self.instance_as_budget:
            prev_budget = int(self.all_budgets[self.stage - 1]) if self.stage > 0 else 0
            curr_insts = self.inst_seed_pairs[int(prev_budget):int(curr_budget)]
        else:
            curr_insts = self.inst_seed_pairs
        n_insts_remaining = len(curr_insts) - self.curr_inst_idx - 1

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

        # get incumbent if all instances have been evaluated
        if n_insts_remaining <= 0:
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