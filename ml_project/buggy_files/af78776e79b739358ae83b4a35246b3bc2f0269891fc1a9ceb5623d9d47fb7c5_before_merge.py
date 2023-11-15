    def __enter__(self):
        """
        Performs some basic checks and returns itself when everything is ready to invoke a Lambda function.

        :returns InvokeContext: Returns this object
        """

        # Grab template from file and create a provider
        self._template_dict = self._get_template_data(self._template_file)
        self._function_provider = SamFunctionProvider(self._template_dict, self.parameter_overrides)

        self._env_vars_value = self._get_env_vars_value(self._env_vars_file)
        self._log_file_handle = self._setup_log_file(self._log_file)

        self._debug_context = self._get_debug_context(self._debug_ports, self._debug_args, self._debugger_path)

        self._container_manager = self._get_container_manager(self._docker_network, self._skip_pull_image)

        if not self._container_manager.is_docker_reachable:
            raise InvokeContextException("Running AWS SAM projects locally requires Docker. Have you got it installed?")

        return self