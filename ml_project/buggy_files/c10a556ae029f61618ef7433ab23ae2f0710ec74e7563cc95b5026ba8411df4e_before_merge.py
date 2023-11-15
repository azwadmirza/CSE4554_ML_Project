    def start(self, config, instance,
              cutoff=None,
              memory_limit=None,
              seed=12345,
              instance_specific="0"):
        """
            wrapper function for ExecuteTARun.run() to check configuration budget before the runs
            and to update stats after run

            Parameters
            ----------
                config : dictionary
                    dictionary param -> value
                instance : string
                    problem instance
                cutoff : double
                    runtime cutoff
                seed : int
                    random seed
                instance_specific: str
                    instance specific information (e.g., domain file or solution)

            Returns
            -------
                status: enum of StatusType (int)
                    {SUCCESS, TIMEOUT, CRASHED, ABORT}
                cost: float
                    cost/regret/quality (float) (None, if not returned by TA)
                runtime: float
                    runtime (None if not returned by TA)
                additional_info: dict
                    all further additional run information
        """

        if self.stats.is_budget_exhausted():
            self.logger.debug(
                "Skip target algorithm run due to exhausted configuration budget")
            return StatusType.ABORT, np.nan, 0, {"misc": "exhausted bugdet -- ABORT"}

        if cutoff is not None:
            cutoff = int(math.ceil(cutoff))
        if memory_limit is not None:
            memory_limit = int(math.ceil(memory_limit))

        additional_arguments = {}

        if self._supports_memory_limit is True:
            additional_arguments['memory_limit'] = memory_limit
        else:
            raise ValueError('Target algorithm executor %s does not support '
                             'restricting the memory usage.' %
                             self.__class__.__name__)

        status, cost, runtime, additional_info = self.run(config=config,
                                                          instance=instance,
                                                          cutoff=cutoff,
                                                          seed=seed,
                                                          instance_specific=instance_specific,
                                                          **additional_arguments)
        # update SMAC stats
        self.stats.ta_runs += 1
        self.stats.ta_time_used += float(runtime)

        self.logger.debug("Return: Status: %d, cost: %f, time. %f, additional: %s" % (
            status, cost, runtime, str(additional_info)))

        return status, cost, runtime, additional_info