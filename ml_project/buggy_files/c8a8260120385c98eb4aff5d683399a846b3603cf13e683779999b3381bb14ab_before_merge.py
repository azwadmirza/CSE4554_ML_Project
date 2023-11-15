    def daemonize_if_required(self):
        if self.options.daemon:
            # Late import so logging works correctly
            import salt.utils
            salt.utils.daemonize()