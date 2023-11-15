    def prepare_execution(self, func_arn, env_vars, runtime, command, handler, lambda_cwd):
        entrypoint = ''
        if command:
            entrypoint = ' --entrypoint ""'
        else:
            command = '"%s"' % handler

        # add Docker Lambda env vars
        network = config.LAMBDA_DOCKER_NETWORK
        network_str = '--network="%s"' % network if network else ''
        if network == 'host':
            port = str(self.next_port + self.port_offset)
            env_vars['DOCKER_LAMBDA_API_PORT'] = port
            env_vars['DOCKER_LAMBDA_RUNTIME_PORT'] = port
            self.next_port = (self.next_port + 1) % self.max_port

        env_vars_string = ' '.join(['-e {}="${}"'.format(k, k) for (k, v) in env_vars.items()])
        debug_docker_java_port = '-p {p}:{p}'.format(p=Util.debug_java_port) if Util.debug_java_port else ''
        docker_cmd = self._docker_cmd()
        docker_image = Util.docker_image_for_runtime(runtime)
        rm_flag = Util.get_docker_remove_flag()

        if config.LAMBDA_REMOTE_DOCKER:
            cmd = (
                'CONTAINER_ID="$(%s create -i'
                ' %s'  # entrypoint
                ' %s'  # debug_docker_java_port
                ' %s'  # env
                ' %s'  # network
                ' %s'  # --rm flag
                ' %s %s'  # image and command
                ')";'
                '%s cp "%s/." "$CONTAINER_ID:/var/task"; '
                '%s start -ai "$CONTAINER_ID";'
            ) % (docker_cmd, entrypoint, debug_docker_java_port, env_vars_string, network_str, rm_flag,
                 docker_image, command,
                 docker_cmd, lambda_cwd,
                 docker_cmd)
        else:
            lambda_cwd_on_host = Util.get_host_path_for_path_in_docker(lambda_cwd)
            cmd = (
                '%s run -i'
                ' %s -v "%s":/var/task'
                ' %s'
                ' %s'  # network
                ' %s'  # --rm flag
                ' %s %s'
            ) % (docker_cmd, entrypoint, lambda_cwd_on_host, env_vars_string,
                 network_str, rm_flag, docker_image, command)
        return cmd