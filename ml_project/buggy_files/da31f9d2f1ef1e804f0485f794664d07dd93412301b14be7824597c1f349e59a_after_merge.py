    def check_task_is_cached(self, state: State, inputs: Dict[str, Result]) -> State:
        """
        Checks if task is cached and whether the cache is still valid.

        Args:
            - state (State): the current state of this task
            - inputs (Dict[str, Result]): a dictionary of inputs whose keys correspond
                to the task's `run()` arguments.

        Returns:
            - State: the state of the task after running the check

        Raises:
            - ENDRUN: if the task is not ready to run
        """
        if state.is_cached():
            assert isinstance(state, Cached)  # mypy assert
            sanitized_inputs = {key: res.value for key, res in inputs.items()}
            if self.task.cache_validator(
                state, sanitized_inputs, prefect.context.get("parameters")
            ):
                state._result = state._result.to_result(self.task.result_handler)
                return state
            else:
                state = Pending("Cache was invalid; ready to run.")

        if self.task.cache_for is not None:
            candidate_states = []
            if prefect.context.get("caches"):
                candidate_states = prefect.context.caches.get(
                    self.task.cache_key or self.task.name, []
                )
            sanitized_inputs = {key: res.value for key, res in inputs.items()}
            for candidate in candidate_states:
                if self.task.cache_validator(
                    candidate, sanitized_inputs, prefect.context.get("parameters")
                ):
                    candidate._result = candidate._result.to_result(
                        self.task.result_handler
                    )
                    return candidate

        if self.task.cache_for is not None:
            self.logger.warning(
                "Task '{name}': can't use cache because it "
                "is now invalid".format(
                    name=prefect.context.get("task_full_name", self.task.name)
                )
            )
        return state or Pending("Cache was invalid; ready to run.")