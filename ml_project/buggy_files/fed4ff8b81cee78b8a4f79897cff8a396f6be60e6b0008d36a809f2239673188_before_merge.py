    def _run_on_schedule(
        self, parameters: Dict[str, Any], runner_cls: type, **kwargs: Any
    ) -> "prefect.engine.state.State":

        base_parameters = parameters or dict()

        ## determine time of first run
        try:
            if self.schedule is not None:
                next_run_event = self.schedule.next(1, return_events=True)[0]
                next_run_time = next_run_event.start_time  # type: ignore
                parameters = base_parameters.copy()
                parameters.update(next_run_event.parameter_defaults)  # type: ignore
            else:
                next_run_time = pendulum.now("utc")
        except IndexError:
            raise ValueError("Flow has no more scheduled runs.") from None

        ## setup initial states
        flow_state = prefect.engine.state.Scheduled(start_time=next_run_time, result={})
        flow_state = kwargs.pop("state", flow_state)
        if not isinstance(flow_state.result, dict):
            flow_state.result = {}
        task_states = kwargs.pop("task_states", {})
        flow_state.result.update(task_states)

        # set context for this flow run
        flow_run_context = kwargs.pop(
            "context", {}
        ).copy()  # copy to avoid modification

        ## run this flow indefinitely, so long as its schedule has future dates
        while True:

            flow_run_context.update(scheduled_start_time=next_run_time)

            if flow_state.is_scheduled():
                next_run_time = flow_state.start_time
                now = pendulum.now("utc")
                naptime = max((next_run_time - now).total_seconds(), 0)
                if naptime > 0:
                    self.logger.info(
                        "Waiting for next scheduled run at {}".format(next_run_time)
                    )
                time.sleep(naptime)

            ## begin a single flow run
            while not flow_state.is_finished():
                runner = runner_cls(flow=self)
                flow_state = runner.run(
                    parameters=parameters,
                    return_tasks=self.tasks,
                    state=flow_state,
                    task_states=flow_state.result,
                    context=flow_run_context,
                    **kwargs
                )
                if not isinstance(flow_state.result, dict):
                    return flow_state  # something went wrong

                task_states = list(flow_state.result.values())
                for s in filter(lambda x: x.is_mapped(), task_states):
                    task_states.extend(s.map_states)
                earliest_start = min(
                    [s.start_time for s in task_states if s.is_scheduled()],
                    default=pendulum.now("utc"),
                )

                ## wait until first task is ready for retry
                now = pendulum.now("utc")
                naptime = max((earliest_start - now).total_seconds(), 0)
                if naptime > 0:
                    self.logger.info(
                        "Waiting for next available Task run at {}".format(
                            earliest_start
                        )
                    )
                time.sleep(naptime)

            ## create next scheduled run
            try:
                # update context cache
                for t, s in flow_state.result.items():
                    if s.is_cached():
                        cached_sub_states = [s]
                    elif s.is_mapped() and any(
                        sub_state.is_cached() for sub_state in s.map_states
                    ):
                        cached_sub_states = [
                            sub_state
                            for sub_state in s.map_states
                            if sub_state.is_cached()
                        ]
                    else:
                        cached_sub_states = []

                    fresh_states = [
                        s
                        for s in prefect.context.caches.get(t.cache_key or t.name, [])
                        + cached_sub_states
                        if s.cached_result_expiration > now
                    ]
                    prefect.context.caches[t.cache_key or t.name] = fresh_states
                if self.schedule is not None:
                    next_run_event = self.schedule.next(1, return_events=True)[0]
                    next_run_time = next_run_event.start_time  # type: ignore
                    parameters = base_parameters.copy()
                    parameters.update(next_run_event.parameter_defaults)  # type: ignore
                else:
                    break
            except IndexError:
                break
            flow_state = prefect.engine.state.Scheduled(
                start_time=next_run_time, result={}
            )
        return flow_state