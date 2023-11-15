    def _enforce_limits(self, **kw):
        """
            Enforces any limits that may be imposed by the configuration.
        """

        # if kernels-per-user is configured, ensure that this next kernel is still within the limit
        max_kernels_per_user = self.kernel_manager.parent.parent.max_kernels_per_user
        if max_kernels_per_user >= 0:
            env_dict = kw.get('env')
            username = env_dict['KERNEL_USERNAME']
            current_kernel_count = self.kernel_manager.parent.parent.kernel_session_manager.active_sessions(username)
            if current_kernel_count >= max_kernels_per_user:
                error_message = "A max kernels per user limit has been set to {} and user '{}' currently has {} " \
                                "active {}.".format(max_kernels_per_user, username, current_kernel_count,
                                                    "kernel" if max_kernels_per_user == 1 else "kernels")
                self.log_and_raise(http_status_code=403, reason=error_message)