    def _update_stage(self, run_history: RunHistory) -> None:
        """
        Update tracking information for a new stage/iteration and update statistics.
        This method is called to initialize stage variables and after all configurations
        of a successive halving stage are completed.

        Parameters
        ----------
         run_history : smac.runhistory.runhistory.RunHistory
            stores all runs we ran so far
        """

        if not hasattr(self, 'stage'):
            # initialize all relevant variables for first run
            # (this initialization is not a part of init because hyperband uses the same init method and has a )
            # to track iteration and stage
            self.sh_iters = 0
            self.stage = 0
            # to track challengers across stages
            self.configs_to_run = []  # type: typing.List[Configuration]
            self.curr_inst_idx = 0
            self.running_challenger = None
            self.success_challengers = set()  # successful configs
            self.do_not_advance_challengers = set()  # configs which are successful, but should not be advanced
            self.fail_challengers = set()  # capped configs and other failures
            self.fail_chal_offset = 0

        else:
            self.stage += 1
            # only uncapped challengers are considered valid for the next iteration
            valid_challengers = list(
                (self.success_challengers | self.do_not_advance_challengers) - self.fail_challengers
            )

            if self.stage < len(self.all_budgets) and len(valid_challengers) > 0:
                # if this is the next stage in same iteration,
                # use top 'k' from the evaluated configurations for next iteration

                # determine 'k' for the next iteration - at least 1
                next_n_chal = int(max(1, self.n_configs_in_stage[self.stage]))
                # selecting the top 'k' challengers for the next iteration
                configs_to_run = self._top_k(configs=valid_challengers,
                                             run_history=run_history,
                                             k=next_n_chal)
                self.configs_to_run = [
                    config for config in configs_to_run
                    if config not in self.do_not_advance_challengers
                ]
                # if some runs were capped, top_k returns less than the required configurations
                # to handle that, we keep track of how many configurations are missing
                # (since they are technically failed here too)
                missing_challengers = int(self.n_configs_in_stage[self.stage]) - len(self.configs_to_run)
                if missing_challengers > 0:
                    self.fail_chal_offset = missing_challengers
                else:
                    self.fail_chal_offset = 0
                if next_n_chal == missing_challengers:
                    next_stage = True
                    self.logger.info('Successive Halving iteration-step: %d-%d with '
                                     'budget [%.2f / %d] - expected %d new challenger(s), but '
                                     'no configurations propagated to the next budget.',
                                     self.sh_iters + 1, self.stage + 1, self.all_budgets[self.stage],
                                     self.max_budget, self.n_configs_in_stage[self.stage])
                else:
                    next_stage = False
            else:
                next_stage = True

            if next_stage:
                # update stats for the prev iteration
                self.stats.update_average_configs_per_intensify(n_configs=self._chall_indx)

                # reset stats for the new iteration
                self._ta_time = 0
                self._chall_indx = 0
                self.num_run = 0

                self.iteration_done = True
                self.sh_iters += 1
                self.stage = 0
                self.run_tracker = []
                self.configs_to_run = []
                self.fail_chal_offset = 0

                # randomize instance-seed pairs per successive halving run, if user specifies
                if self.instance_order == 'shuffle':
                    self.rs.shuffle(self.inst_seed_pairs)

        # to track configurations for the next stage
        self.success_challengers = set()  # successful configs
        self.do_not_advance_challengers = set()  # successful, but should not be advanced to the next budget/stage
        self.fail_challengers = set()  # capped/failed configs
        self.curr_inst_idx = 0
        self.running_challenger = None