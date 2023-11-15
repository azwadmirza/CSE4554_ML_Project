    def _make_tmp_path(self, remote_user=None):
        '''
        Create and return a temporary path on a remote box.
        '''

        if remote_user is None:
            remote_user = self._play_context.remote_user

        try:
            admin_users = self._connection._shell.get_option('admin_users') + [remote_user]
        except AnsibleError:
            admin_users = ['root', remote_user]  # plugin does not support admin_users
        try:
            remote_tmp = self._connection._shell.get_option('remote_tmp')
        except AnsibleError:
            remote_tmp = '~/.ansible/tmp'

        # deal with tmpdir creation
        basefile = 'ansible-tmp-%s-%s' % (time.time(), random.randint(0, 2**48))
        use_system_tmp = bool(self._play_context.become and self._play_context.become_user not in admin_users)
        # Network connection plugins (network_cli, netconf, etc.) execute on the controller, rather than the remote host.
        # As such, we want to avoid using remote_user for paths  as remote_user may not line up with the local user
        # This is a hack and should be solved by more intelligent handling of remote_tmp in 2.7
        if getattr(self._connection, '_remote_is_local', False):
            tmpdir = C.DEFAULT_LOCAL_TMP
        else:
            tmpdir = self._remote_expand_user(remote_tmp, sudoable=False)
        cmd = self._connection._shell.mkdtemp(basefile=basefile, system=use_system_tmp, tmpdir=tmpdir)
        result = self._low_level_execute_command(cmd, sudoable=False)

        # error handling on this seems a little aggressive?
        if result['rc'] != 0:
            if result['rc'] == 5:
                output = 'Authentication failure.'
            elif result['rc'] == 255 and self._connection.transport in ('ssh',):

                if self._play_context.verbosity > 3:
                    output = u'SSH encountered an unknown error. The output was:\n%s%s' % (result['stdout'], result['stderr'])
                else:
                    output = (u'SSH encountered an unknown error during the connection. '
                              'We recommend you re-run the command using -vvvv, which will enable SSH debugging output to help diagnose the issue')

            elif u'No space left on device' in result['stderr']:
                output = result['stderr']
            else:
                output = ('Authentication or permission failure. '
                          'In some cases, you may have been able to authenticate and did not have permissions on the target directory. '
                          'Consider changing the remote tmp path in ansible.cfg to a path rooted in "/tmp". '
                          'Failed command was: %s, exited with result %d' % (cmd, result['rc']))
            if 'stdout' in result and result['stdout'] != u'':
                output = output + u", stdout output: %s" % result['stdout']
            if self._play_context.verbosity > 3 and 'stderr' in result and result['stderr'] != u'':
                output += u", stderr output: %s" % result['stderr']
            raise AnsibleConnectionFailure(output)
        else:
            self._cleanup_remote_tmp = True

        try:
            stdout_parts = result['stdout'].strip().split('%s=' % basefile, 1)
            rc = self._connection._shell.join_path(stdout_parts[-1], u'').splitlines()[-1]
        except IndexError:
            # stdout was empty or just space, set to / to trigger error in next if
            rc = '/'

        # Catch failure conditions, files should never be
        # written to locations in /.
        if rc == '/':
            raise AnsibleError('failed to resolve remote temporary directory from %s: `%s` returned empty string' % (basefile, cmd))

        self._connection._shell.tmpdir = rc

        if not use_system_tmp:
            self._connection._shell.env.update({'ANSIBLE_REMOTE_TMP': self._connection._shell.tmpdir})
        return rc