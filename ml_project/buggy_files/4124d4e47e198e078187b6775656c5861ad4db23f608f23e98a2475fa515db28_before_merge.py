    def user_run_dir(self):
        # Try to ensure that (/var)/run/user/$(id -u) exists so that
        #  `gpgconf --create-socketdir` can be run later.
        #
        # NOTE(opadron): This action helps prevent a large class of
        #                "file-name-too-long" errors in gpg.

        try:
            has_suitable_gpgconf = bool(_GpgConstants.gpgconf_string)
        except SpackGPGError:
            has_suitable_gpgconf = False

        # If there is no suitable gpgconf, don't even bother trying to
        # precreate a user run dir.
        if not has_suitable_gpgconf:
            return None

        result = None
        for var_run in ('/run', '/var/run'):
            if not os.path.exists(var_run):
                continue

            var_run_user = os.path.join(var_run, 'user')
            try:
                if not os.path.exists(var_run_user):
                    os.mkdir(var_run_user)
                    os.chmod(var_run_user, 0o777)

                user_dir = os.path.join(var_run_user, str(os.getuid()))

                if not os.path.exists(user_dir):
                    os.mkdir(user_dir)
                    os.chmod(user_dir, 0o700)

            # If the above operation fails due to lack of permissions, then
            # just carry on without running gpgconf and hope for the best.
            #
            # NOTE(opadron): Without a dir in which to create a socket for IPC,
            #                gnupg may fail if GNUPGHOME is set to a path that
            #                is too long, where "too long" in this context is
            #                actually quite short; somewhere in the
            #                neighborhood of more than 100 characters.
            #
            # TODO(opadron): Maybe a warning should be printed in this case?
            except OSError as exc:
                if exc.errno not in (errno.EPERM, errno.EACCES):
                    raise
                user_dir = None

            # return the last iteration that provides a usable user run dir
            if user_dir is not None:
                result = user_dir

        return result