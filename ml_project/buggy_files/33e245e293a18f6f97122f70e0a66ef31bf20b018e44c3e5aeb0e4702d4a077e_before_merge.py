    def wait_for_pipeline_state(
        self,
        pipeline_name: str,
        pipeline_id: str,
        instance_url: str,
        namespace: str = "default",
        success_states: Optional[List[str]] = None,
        failure_states: Optional[List[str]] = None,
        timeout: int = 5 * 60,
    ):
        """
        Polls pipeline state and raises an exception if the state is one of
        `failure_states` or the operation timeouted.
        """
        failure_states = failure_states or FAILURE_STATES
        success_states = success_states or SUCCESS_STATES
        start_time = monotonic()
        current_state = None
        while monotonic() - start_time < timeout:
            current_state = self._get_workflow_state(
                pipeline_name=pipeline_name,
                pipeline_id=pipeline_id,
                instance_url=instance_url,
                namespace=namespace,
            )

            if current_state in success_states:
                return
            if current_state in failure_states:
                raise AirflowException(
                    f"Pipeline {pipeline_name} state {current_state} is not "
                    f"one of {success_states}"
                )
            sleep(30)

        # Time is up!
        raise AirflowException(
            f"Pipeline {pipeline_name} state {current_state} is not "
            f"one of {success_states} after {timeout}s"
        )