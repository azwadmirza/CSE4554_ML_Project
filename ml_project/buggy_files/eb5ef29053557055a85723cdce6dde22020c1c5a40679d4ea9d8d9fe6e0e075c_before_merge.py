    def _parse_kwargs(self, user_kwargs: dict, check_envars: bool = False) -> tuple:
        """
        Parse the kwargs passed in and separate them out for `register_task_definition`
        and `run_task`. This is required because boto3 does not allow extra kwargs
        and if they are provided it will raise botocore.exceptions.ParamValidationError.

        Args:
            - user_kwargs (dict): The kwargs passed to the initialization of the environment
            - check_envars (bool): Whether to check envars for kwargs

        Returns:
            tuple: a tuple of three dictionaries (task_definition_kwargs, task_run_kwargs,
              container_definitions_kwargs)
        """
        definition_kwarg_list = [
            "taskRoleArn",
            "executionRoleArn",
            "volumes",
            "placementConstraints",
            "cpu",
            "memory",
            "tags",
            "pidMode",
            "ipcMode",
            "proxyConfiguration",
            "inferenceAccelerators",
        ]

        definition_kwarg_list_no_eval = ["cpu", "memory"]

        run_kwarg_list = [
            "cluster",
            "count",
            "startedBy",
            "group",
            "placementConstraints",
            "placementStrategy",
            "platformVersion",
            "networkConfiguration",
            "tags",
            "enableECSManagedTags",
            "propagateTags",
        ]

        container_definitions_kwarg_list = [
            "mountPoints",
            "secrets",
            "environment",
            "logConfiguration",
            "repositoryCredentials",
        ]

        task_definition_kwargs = {}
        definition_kwarg_list_eval = {
            i: (i not in definition_kwarg_list_no_eval) for i in definition_kwarg_list
        }
        for key, item in user_kwargs.items():
            if key in definition_kwarg_list:
                if definition_kwarg_list_eval.get(key):
                    try:
                        # Parse kwarg if needed
                        item = literal_eval(item)
                    except (ValueError, SyntaxError):
                        pass
                task_definition_kwargs.update({key: item})
                self.logger.debug("{} = {}".format(key, item))

        task_run_kwargs = {}
        for key, item in user_kwargs.items():
            if key in run_kwarg_list:
                try:
                    # Parse kwarg if needed
                    item = literal_eval(item)
                except (ValueError, SyntaxError):
                    pass
                task_run_kwargs.update({key: item})
                self.logger.debug("{} = {}".format(key, item))

        container_definitions_kwargs = {}
        for key, item in user_kwargs.get("containerDefinitions", [{}])[0].items():
            if key in container_definitions_kwarg_list:
                try:
                    # Parse kwarg if needed
                    item = literal_eval(item)
                except (ValueError, SyntaxError):
                    pass
                container_definitions_kwargs.update({key: item})
                self.logger.debug("{} = {}".format(key, item))

        # Check environment if keys were not provided
        if check_envars:
            for key in definition_kwarg_list:
                if not task_definition_kwargs.get(key) and os.getenv(key):
                    self.logger.debug("{} from environment variable".format(key))
                    def_env_value = os.getenv(key)
                    if definition_kwarg_list_eval.get(key):
                        try:
                            # Parse env var if needed
                            def_env_value = literal_eval(def_env_value)  # type: ignore
                        except (ValueError, SyntaxError):
                            pass
                    task_definition_kwargs.update({key: def_env_value})

            for key in run_kwarg_list:
                if not task_run_kwargs.get(key) and os.getenv(key):
                    self.logger.debug("{} from environment variable".format(key))
                    run_env_value = os.getenv(key)
                    try:
                        # Parse env var if needed
                        run_env_value = literal_eval(run_env_value)  # type: ignore
                    except (ValueError, SyntaxError):
                        pass
                    task_run_kwargs.update({key: run_env_value})

            for key in container_definitions_kwarg_list:
                if not container_definitions_kwargs.get(key) and os.getenv(
                    "containerDefinitions_{}".format(key)
                ):
                    self.logger.debug(
                        "Container definition: {} from environment variable".format(key)
                    )
                    cd_env_value = os.getenv("containerDefinitions_{}".format(key))
                    try:
                        # Parse env var if needed
                        cd_env_value = literal_eval(cd_env_value)  # type: ignore
                    except (ValueError, SyntaxError):
                        pass
                    container_definitions_kwargs.update({key: cd_env_value})

        return task_definition_kwargs, task_run_kwargs, container_definitions_kwargs