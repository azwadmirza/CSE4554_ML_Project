    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)

        # Note: docker supports running as non-root in some configurations.
        # (For instance, setting the UNIX socket file to be readable and
        # writable by a specific UNIX group and then putting users into that
        # group).  Therefore we don't check that the user is root when using
        # this connection.  But if the user is getting a permission denied
        # error it probably means that docker on their system is only
        # configured to be connected to by root and they are not running as
        # root.

        if 'docker_command' in kwargs:
            self.docker_cmd = kwargs['docker_command']
        else:
            self.docker_cmd = distutils.spawn.find_executable('docker')
            if not self.docker_cmd:
                raise AnsibleError("docker command not found in PATH")

        docker_version = self._get_docker_version()
        if LooseVersion(docker_version) < LooseVersion(u'1.3'):
            raise AnsibleError('docker connection type requires docker 1.3 or higher')

        # The remote user we will request from docker (if supported)
        self.remote_user = None
        # The actual user which will execute commands in docker (if known)
        self.actual_user = None

        if self._play_context.remote_user is not None:
            if LooseVersion(docker_version) >= LooseVersion(u'1.7'):
                # Support for specifying the exec user was added in docker 1.7
                self.remote_user = self._play_context.remote_user
                self.actual_user = self.remote_user
            else:
                self.actual_user = self._get_docker_remote_user()

                if self.actual_user != self._play_context.remote_user:
                    display.warning(u'docker {0} does not support remote_user, using container default: {1}'
                                    .format(docker_version, self.actual_user or u'?'))
        elif self._display.verbosity > 2:
            # Since we're not setting the actual_user, look it up so we have it for logging later
            # Only do this if display verbosity is high enough that we'll need the value
            # This saves overhead from calling into docker when we don't need to
            self.actual_user = self._get_docker_remote_user()