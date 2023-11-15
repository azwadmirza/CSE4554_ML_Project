    def start_raylet(self, use_valgrind=False, use_profiler=False):
        """Start the raylet.

        Args:
            use_valgrind (bool): True if we should start the process in
                valgrind.
            use_profiler (bool): True if we should start the process in the
                valgrind profiler.
        """
        stdout_file, stderr_file = self.new_log_files("raylet")
        process_info = ray.services.start_raylet(
            self._redis_address,
            self._node_ip_address,
            self._ray_params.node_manager_port,
            self._raylet_socket_name,
            self._plasma_store_socket_name,
            self._ray_params.worker_path,
            self._temp_dir,
            self._session_dir,
            self.get_resource_spec(),
            self._ray_params.min_worker_port,
            self._ray_params.max_worker_port,
            self._ray_params.object_manager_port,
            self._ray_params.redis_password,
            use_valgrind=use_valgrind,
            use_profiler=use_profiler,
            stdout_file=stdout_file,
            stderr_file=stderr_file,
            config=self._config,
            include_java=self._ray_params.include_java,
            java_worker_options=self._ray_params.java_worker_options,
            load_code_from_local=self._ray_params.load_code_from_local,
            fate_share=self.kernel_fate_share)
        assert ray_constants.PROCESS_TYPE_RAYLET not in self.all_processes
        self.all_processes[ray_constants.PROCESS_TYPE_RAYLET] = [process_info]