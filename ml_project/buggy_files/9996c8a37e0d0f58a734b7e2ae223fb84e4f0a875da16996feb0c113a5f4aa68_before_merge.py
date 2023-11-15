    def _fixup_perms2(self, remote_paths, remote_user=None, execute=True):
        """
        We need the files we upload to be readable (and sometimes executable)
        by the user being sudo'd to but we want to limit other people's access
        (because the files could contain passwords or other private
        information.  We achieve this in one of these ways:

        * If no sudo is performed or the remote_user is sudo'ing to
          themselves, we don't have to change permissions.
        * If the remote_user sudo's to a privileged user (for instance, root),
          we don't have to change permissions
        * If the remote_user sudo's to an unprivileged user then we attempt to
          grant the unprivileged user access via file system acls.
        * If granting file system acls fails we try to change the owner of the
          file with chown which only works in case the remote_user is
          privileged or the remote systems allows chown calls by unprivileged
          users (e.g. HP-UX)
        * If the chown fails we can set the file to be world readable so that
          the second unprivileged user can read the file.
          Since this could allow other users to get access to private
          information we only do this if ansible is configured with
          "allow_world_readable_tmpfiles" in the ansible.cfg
        """
        if remote_user is None:
            remote_user = self._play_context.remote_user

        if self._connection._shell.SHELL_FAMILY == 'powershell':
            # This won't work on Powershell as-is, so we'll just completely skip until
            # we have a need for it, at which point we'll have to do something different.
            return remote_paths

        try:
            admin_users = self._connection._shell.get_option('admin_users')
        except AnsibleError:
            admin_users = ['root']  # plugin does not support admin users

        if self._play_context.become and self._play_context.become_user and self._play_context.become_user not in admin_users + [remote_user]:
            # Unprivileged user that's different than the ssh user.  Let's get
            # to work!

            # Try to use file system acls to make the files readable for sudo'd
            # user
            if execute:
                chmod_mode = 'rx'
                setfacl_mode = 'r-x'
            else:
                chmod_mode = 'rX'
                # NOTE: this form fails silently on freebsd.  We currently
                # never call _fixup_perms2() with execute=False but if we
                # start to we'll have to fix this.
                setfacl_mode = 'r-X'

            res = self._remote_set_user_facl(remote_paths, self._play_context.become_user, setfacl_mode)
            if res['rc'] != 0:
                # File system acls failed; let's try to use chown next
                # Set executable bit first as on some systems an
                # unprivileged user can use chown
                if execute:
                    res = self._remote_chmod(remote_paths, 'u+x')
                    if res['rc'] != 0:
                        raise AnsibleError('Failed to set file mode on remote temporary files (rc: {0}, err: {1})'.format(res['rc'], to_native(res['stderr'])))

                res = self._remote_chown(remote_paths, self._play_context.become_user)
                if res['rc'] != 0 and remote_user in admin_users:
                    # chown failed even if remove_user is root
                    raise AnsibleError('Failed to change ownership of the temporary files Ansible needs to create despite connecting as a privileged user. '
                                       'Unprivileged become user would be unable to read the file.')
                elif res['rc'] != 0:
                    if C.ALLOW_WORLD_READABLE_TMPFILES:
                        # chown and fs acls failed -- do things this insecure
                        # way only if the user opted in in the config file
                        display.warning('Using world-readable permissions for temporary files Ansible needs to create when becoming an unprivileged user. '
                                        'This may be insecure. For information on securing this, see '
                                        'https://docs.ansible.com/ansible/become.html#becoming-an-unprivileged-user')
                        res = self._remote_chmod(remote_paths, 'a+%s' % chmod_mode)
                        if res['rc'] != 0:
                            raise AnsibleError('Failed to set file mode on remote files (rc: {0}, err: {1})'.format(res['rc'], to_native(res['stderr'])))
                    else:
                        raise AnsibleError('Failed to set permissions on the temporary files Ansible needs to create when becoming an unprivileged user '
                                           '(rc: %s, err: %s}). For information on working around this, see '
                                           'https://docs.ansible.com/ansible/become.html#becoming-an-unprivileged-user'
                                           % (res['rc'], to_native(res['stderr'])))
        elif execute:
            # Can't depend on the file being transferred with execute permissions.
            # Only need user perms because no become was used here
            res = self._remote_chmod(remote_paths, 'u+x')
            if res['rc'] != 0:
                raise AnsibleError('Failed to set execute bit on remote files (rc: {0}, err: {1})'.format(res['rc'], to_native(res['stderr'])))

        return remote_paths