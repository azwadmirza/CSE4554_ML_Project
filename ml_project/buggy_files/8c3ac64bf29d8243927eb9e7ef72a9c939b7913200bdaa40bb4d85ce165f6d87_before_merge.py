    def _build_exec_cmd(self, cmd):
        """ Build the local kubectl exec command to run cmd on remote_host
        """
        local_cmd = [self.transport_cmd]
        censored_local_cmd = [self.transport_cmd]

        # Build command options based on doc string
        doc_yaml = AnsibleLoader(self.documentation).get_single_data()
        for key in doc_yaml.get('options'):
            if key.endswith('verify_ssl') and self.get_option(key) != '':
                # Translate verify_ssl to skip_verify_ssl, and output as string
                skip_verify_ssl = not self.get_option(key)
                local_cmd.append(u'{0}={1}'.format(self.connection_options[key], str(skip_verify_ssl).lower()))
                censored_local_cmd.append(u'{0}={1}'.format(self.connection_options[key], str(skip_verify_ssl).lower()))
            elif not key.endswith('container') and self.get_option(key) and self.connection_options.get(key):
                cmd_arg = self.connection_options[key]
                local_cmd += [cmd_arg, self.get_option(key)]
                # Redact password and token from console log
                if key.endswith(('_token', '_password')):
                    censored_local_cmd += [cmd_arg, '*' * 8]

        extra_args_name = u'{0}_extra_args'.format(self.transport)
        if self.get_option(extra_args_name):
            local_cmd += self.get_option(extra_args_name).split(' ')
            censored_local_cmd += self.get_option(extra_args_name).split(' ')

        pod = self.get_option(u'{0}_pod'.format(self.transport))
        if not pod:
            pod = self._play_context.remote_addr
        # -i is needed to keep stdin open which allows pipelining to work
        local_cmd += ['exec', '-i', pod]
        censored_local_cmd += ['exec', '-i', pod]

        # if the pod has more than one container, then container is required
        container_arg_name = u'{0}_container'.format(self.transport)
        if self.get_option(container_arg_name):
            local_cmd += ['-c', self.get_option(container_arg_name)]
            censored_local_cmd += ['-c', self.get_option(container_arg_name)]

        local_cmd += ['--'] + cmd
        censored_local_cmd += ['--'] + cmd

        return local_cmd