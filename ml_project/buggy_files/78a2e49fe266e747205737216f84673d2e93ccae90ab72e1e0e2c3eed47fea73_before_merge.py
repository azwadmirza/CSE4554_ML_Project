    def _get_runs(self,
                  configs: Union[str, typing.List[Configuration]],
                  insts: Union[str, typing.List[str]],
                  repetitions: int = 1,
                  runhistory: RunHistory = None,
                  ) -> typing.Tuple[typing.List[_Run], RunHistory]:
        """
        Generate list of SMAC-TAE runs to be executed. This means
        combinations of configs with all instances on a certain number of seeds.

        side effect: Adds runs that don't need to be reevaluated to self.rh!

        Parameters
        ----------
        configs: str or list<Configuration>
            string or directly a list of Configuration
            str from [def, inc, def+inc, wallclock_time, cpu_time, all]
                time evaluates at cpu- or wallclock-timesteps of:
                [max_time/2^0, max_time/2^1, max_time/2^3, ..., default]
                with max_time being the highest recorded time
        insts: str or list<str>
            what instances to use for validation, either from
            [train, test, train+test] or directly a list of instances
        repetitions: int
            number of seeds per instance/config-pair to be evaluated
        runhistory: RunHistory
            optional, try to reuse this runhistory and save some runs

        Returns
        -------
        runs: list<_Run>
            list with _Runs
            [_Run(config=CONFIG1,inst=INSTANCE1,seed=SEED1,inst_specs=INST_SPECIFICS1),
             _Run(config=CONFIG2,inst=INSTANCE2,seed=SEED2,inst_specs=INST_SPECIFICS2),
             ...]
        """
        # Get relevant configurations and instances
        if isinstance(configs, str):
            configs = self._get_configs(configs)
        if isinstance(insts, str):
            instances = self._get_instances(insts)  # type: typing.Sequence[typing.Union[str, None]]
        elif insts is not None:
            instances = insts
        else:
            instances = [None]
        # If no instances are given, fix the instances to one "None" instance
        if not instances:
            instances = [None]

        # If algorithm is deterministic, fix repetitions to 1
        if self.scen.deterministic and repetitions != 1:  # type: ignore[attr-defined] # noqa F821
            self.logger.warning("Specified %d repetitions, but fixing to 1, "
                                "because algorithm is deterministic.", repetitions)
            repetitions = 1

        # Extract relevant information from given runhistory
        inst_seed_config = self._process_runhistory(configs, instances, runhistory)

        # Now create the actual run-list
        runs = []
        # Counter for runs without the need of recalculation
        runs_from_rh = 0
        # If we reuse runs, we want to return them as well
        new_rh = RunHistory()

        for i in sorted(instances):
            for rep in range(repetitions):
                # First, find a seed and add all the data we can take from the
                # given runhistory to "our" validation runhistory.
                configs_evaluated = []  # type: Configuration
                if runhistory and i in inst_seed_config:
                    # Choose seed based on most often evaluated inst-seed-pair
                    seed, configs_evaluated = inst_seed_config[i].pop(0)
                    # Delete inst if all seeds are used
                    if not inst_seed_config[i]:
                        inst_seed_config.pop(i)
                    # Add runs to runhistory
                    for c in configs_evaluated[:]:
                        runkey = RunKey(runhistory.config_ids[c], i, seed)
                        cost, time, status, start, end, additional_info = runhistory.data[runkey]
                        if status in [StatusType.CRASHED, StatusType.ABORT, StatusType.CAPPED]:
                            # Not properly executed target algorithm runs should be repeated
                            configs_evaluated.remove(c)
                            continue
                        new_rh.add(c, cost, time, status, instance_id=i,
                                   seed=seed, starttime=start, endtime=end,
                                   additional_info=additional_info)
                        runs_from_rh += 1
                else:
                    # If no runhistory or no entries for instance, get new seed
                    seed = self.rng.randint(MAXINT)

                # We now have a seed and add all configs that are not already
                # evaluated on that seed to the runs-list. This way, we
                # guarantee the same inst-seed-pairs for all configs.
                for config in [c for c in configs if c not in configs_evaluated]:
                    # Only use specifics if specific exists, else use string "0"
                    specs = self.scen.instance_specific[i] if i and i in self.scen.instance_specific else "0"
                    runs.append(_Run(config=config,
                                     inst=i,
                                     seed=seed,
                                     inst_specs=specs))

        self.logger.info("Collected %d runs from %d configurations on %d "
                         "instances with %d repetitions. Reusing %d runs from "
                         "given runhistory.", len(runs), len(configs),
                         len(instances), repetitions, runs_from_rh)

        return runs, new_rh