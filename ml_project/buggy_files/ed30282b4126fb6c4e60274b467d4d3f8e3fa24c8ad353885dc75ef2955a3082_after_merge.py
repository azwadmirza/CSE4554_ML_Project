    def _file_transport_command(self, in_path, out_path, sftp_action):
        # scp and sftp require square brackets for IPv6 addresses, but
        # accept them for hostnames and IPv4 addresses too.
        host = '[%s]' % self.host

        smart_methods = ['sftp', 'scp', 'piped']

        # Windows does not support dd so we cannot use the piped method
        if getattr(self._shell, "_IS_WINDOWS", False):
            smart_methods.remove('piped')

        # Transfer methods to try
        methods = []

        # Use the transfer_method option if set, otherwise use scp_if_ssh
        ssh_transfer_method = self._play_context.ssh_transfer_method
        if ssh_transfer_method is not None:
            if not (ssh_transfer_method in ('smart', 'sftp', 'scp', 'piped')):
                raise AnsibleOptionsError('transfer_method needs to be one of [smart|sftp|scp|piped]')
            if ssh_transfer_method == 'smart':
                methods = smart_methods
            else:
                methods = [ssh_transfer_method]
        else:
            # since this can be a non-bool now, we need to handle it correctly
            scp_if_ssh = C.DEFAULT_SCP_IF_SSH
            if not isinstance(scp_if_ssh, bool):
                scp_if_ssh = scp_if_ssh.lower()
                if scp_if_ssh in BOOLEANS:
                    scp_if_ssh = boolean(scp_if_ssh, strict=False)
                elif scp_if_ssh != 'smart':
                    raise AnsibleOptionsError('scp_if_ssh needs to be one of [smart|True|False]')
            if scp_if_ssh == 'smart':
                methods = smart_methods
            elif scp_if_ssh is True:
                methods = ['scp']
            else:
                methods = ['sftp']

        for method in methods:
            returncode = stdout = stderr = None
            if method == 'sftp':
                cmd = self._build_command(self.get_option('sftp_executable'), to_bytes(host))
                in_data = u"{0} {1} {2}\n".format(sftp_action, shlex_quote(in_path), shlex_quote(out_path))
                in_data = to_bytes(in_data, nonstring='passthru')
                (returncode, stdout, stderr) = self._bare_run(cmd, in_data, checkrc=False)
            elif method == 'scp':
                scp = self.get_option('scp_executable')

                if sftp_action == 'get':
                    cmd = self._build_command(scp, u'{0}:{1}'.format(host, self._shell.quote(in_path)), out_path)
                else:
                    cmd = self._build_command(scp, in_path, u'{0}:{1}'.format(host, self._shell.quote(out_path)))
                in_data = None
                (returncode, stdout, stderr) = self._bare_run(cmd, in_data, checkrc=False)
            elif method == 'piped':
                if sftp_action == 'get':
                    # we pass sudoable=False to disable pty allocation, which
                    # would end up mixing stdout/stderr and screwing with newlines
                    (returncode, stdout, stderr) = self.exec_command('dd if=%s bs=%s' % (in_path, BUFSIZE), sudoable=False)
                    with open(to_bytes(out_path, errors='surrogate_or_strict'), 'wb+') as out_file:
                        out_file.write(stdout)
                else:
                    with open(to_bytes(in_path, errors='surrogate_or_strict'), 'rb') as f:
                        in_data = to_bytes(f.read(), nonstring='passthru')
                    if not in_data:
                        count = ' count=0'
                    else:
                        count = ''
                    (returncode, stdout, stderr) = self.exec_command('dd of=%s bs=%s%s' % (out_path, BUFSIZE, count), in_data=in_data, sudoable=False)

            # Check the return code and rollover to next method if failed
            if returncode == 0:
                return (returncode, stdout, stderr)
            else:
                # If not in smart mode, the data will be printed by the raise below
                if len(methods) > 1:
                    display.warning(u'%s transfer mechanism failed on %s. Use ANSIBLE_DEBUG=1 to see detailed information' % (method, host))
                    display.debug(u'%s' % to_text(stdout))
                    display.debug(u'%s' % to_text(stderr))

        if returncode == 255:
            raise AnsibleConnectionFailure("Failed to connect to the host via %s: %s" % (method, to_native(stderr)))
        else:
            raise AnsibleError("failed to transfer file to %s %s:\n%s\n%s" %
                               (to_native(in_path), to_native(out_path), to_native(stdout), to_native(stderr)))