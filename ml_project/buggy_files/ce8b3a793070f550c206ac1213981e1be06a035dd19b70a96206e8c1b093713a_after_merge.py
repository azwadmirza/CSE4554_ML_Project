    def get_next_run(self,
                     challengers: typing.Optional[typing.List[Configuration]],
                     incumbent: Configuration,
                     chooser: typing.Optional[EPMChooser],
                     run_history: RunHistory,
                     repeat_configs: bool = True,
                     num_workers: int = 1,
                     ) -> typing.Tuple[RunInfoIntent, RunInfo]:
        """
        Selects which challenger to use based on the iteration stage and set the iteration parameters.
        First iteration will choose configurations from the ``chooser`` or input challengers,
        while the later iterations pick top configurations from the previously selected challengers in that iteration

        Parameters
        ----------
        challengers : typing.List[Configuration]
            promising configurations
        incumbent: Configuration
            incumbent configuration
        chooser : smac.optimizer.epm_configuration_chooser.EPMChooser
            optimizer that generates next configurations to use for racing
        run_history : smac.runhistory.runhistory.RunHistory
            stores all runs we ran so far
        repeat_configs : bool
            if False, an evaluated configuration will not be generated again
        num_workers: int
            the maximum number of workers available
            at a given time.

        Returns
        -------
        intent: RunInfoIntent
               Indicator of how to consume the RunInfo object
        run_info: RunInfo
            An object that encapsulates the minimum information to
            evaluate a configuration
         """
        if num_workers > 1:
            warnings.warn("Consider using ParallelSuccesiveHalving instead of "
                          "SuccesiveHalving. The later will halt on each stage "
                          "transition until all configs for the current stage are completed."
                          )
        # if this is the first run, then initialize tracking variables
        if not hasattr(self, 'stage'):
            self._update_stage(run_history=run_history)

        # In the case of multiprocessing, we have runs in Running stage, which have not
        # been processed via process_results(). get_next_run() is called agnostically by
        # smbo. To prevent launching more configs, than the ones needed, we query if
        # there is room for more configurations, else we wait for process_results()
        # to trigger a new stage
        if self._launched_all_configs_for_current_stage(run_history):
            return RunInfoIntent.WAIT, RunInfo(
                config=None,
                instance=None,
                instance_specific="0",
                seed=0,
                cutoff=self.cutoff,
                capped=False,
                budget=0.0,
                source_id=self.identifier,
            )

        # sampling from next challenger marks the beginning of a new iteration
        self.iteration_done = False

        curr_budget = self.all_budgets[self.stage]

        # if all instances have been executed, then reset and move on to next config
        if self.instance_as_budget:
            prev_budget = int(self.all_budgets[self.stage - 1]) if self.stage > 0 else 0
            n_insts = (int(curr_budget) - prev_budget)
        else:
            n_insts = len(self.inst_seed_pairs)

        # In the case of multiprocessing, we will have launched instance/seeds
        # which are not completed, yet running. To proactively move to a new challenger,
        # we account for them in the n_insts_remaining calculation
        running_instances = self._count_running_instances_for_challenger(run_history)

        n_insts_remaining = n_insts - (self.curr_inst_idx + running_instances)

        # if there are instances pending, finish running configuration
        if self.running_challenger and n_insts_remaining > 0:
            challenger = self.running_challenger
            new_challenger = False
        else:
            # select next configuration
            if self.stage == 0:
                # first stage, so sample from configurations/chooser provided
                challenger = self._next_challenger(challengers=challengers,
                                                   chooser=chooser,
                                                   run_history=run_history,
                                                   repeat_configs=repeat_configs)
                if challenger is None:
                    # If no challenger was sampled from the EPM or
                    # initial challengers, it might mean that the EPM
                    # is proposing a configuration that is currently running.
                    # There is a filtering on the above _next_challenger to return
                    # None if the proposed config us already in the run history
                    # To get a new config, we wait for more data
                    return RunInfoIntent.WAIT, RunInfo(
                        config=None,
                        instance=None,
                        instance_specific="0",
                        seed=0,
                        cutoff=self.cutoff,
                        capped=False,
                        budget=0.0,
                        source_id=self.identifier,
                    )

                new_challenger = True
            else:
                # sample top configs from previously sampled configurations
                try:
                    challenger = self.configs_to_run.pop(0)
                    new_challenger = False
                except IndexError:
                    # self.configs_to_run is populated via update_stage,
                    # which is triggered after the completion of a run
                    # If by there are no more configs to run (which is the case
                    # if we run into a IndexError),
                    return RunInfoIntent.SKIP, RunInfo(
                        config=None,
                        instance=None,
                        instance_specific="0",
                        seed=0,
                        cutoff=self.cutoff,
                        capped=False,
                        budget=0.0,
                        source_id=self.identifier,
                    )

            if challenger:
                # reset instance index for the new challenger
                self.curr_inst_idx = 0
                self._chall_indx += 1
                self.running_challenger = challenger
                # If there is a brand new challenger, there will be no
                # running instances
                running_instances = 0

        # calculating the incumbent's performance for adaptive capping
        # this check is required because:
        #   - there is no incumbent performance for the first ever 'intensify' run (from initial design)
        #   - during the 1st intensify run, the incumbent shouldn't be capped after being compared against itself
        if incumbent and incumbent != challenger:
            inc_runs = run_history.get_runs_for_config(incumbent, only_max_observed_budget=True)
            inc_sum_cost = run_history.sum_cost(config=incumbent, instance_seed_budget_keys=inc_runs)
        else:
            inc_sum_cost = np.inf
            if self.first_run:
                self.logger.info("First run, no incumbent provided; challenger is assumed to be the incumbent")
                incumbent = challenger

        # selecting instance-seed subset for this budget, depending on the kind of budget
        if self.instance_as_budget:
            prev_budget = int(self.all_budgets[self.stage - 1]) if self.stage > 0 else 0
            curr_insts = self.inst_seed_pairs[int(prev_budget):int(curr_budget)]
        else:
            curr_insts = self.inst_seed_pairs

        self.logger.debug(" Running challenger  -  %s" % str(challenger))

        # run the next instance-seed pair for the given configuration
        instance, seed = curr_insts[self.curr_inst_idx + running_instances]

        # selecting cutoff if running adaptive capping
        cutoff = self.cutoff
        if self.run_obj_time:
            cutoff = self._adapt_cutoff(challenger=challenger,
                                        run_history=run_history,
                                        inc_sum_cost=inc_sum_cost)
            if cutoff is not None and cutoff <= 0:
                # ran out of time to validate challenger
                self.logger.debug("Stop challenger intensification due to adaptive capping.")
                self.curr_inst_idx = np.inf

        self.logger.debug('Cutoff for challenger: %s' % str(cutoff))

        # For testing purposes, this attribute highlights whether a
        # new challenger is proposed or not. Not required from a functional
        # perspective
        self.new_challenger = new_challenger

        capped = False
        if (self.cutoff is not None) and (cutoff < self.cutoff):  # type: ignore[operator] # noqa F821
            capped = True

        budget = 0.0 if self.instance_as_budget else curr_budget

        self.run_tracker[(challenger, instance, seed, budget)] = False
        return RunInfoIntent.RUN, RunInfo(
            config=challenger,
            instance=instance,
            instance_specific=self.instance_specifics.get(instance, "0"),
            seed=seed,
            cutoff=cutoff,
            capped=capped,
            budget=budget,
            source_id=self.identifier,
        )