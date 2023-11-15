    def create_kernel_manager_and_kernel_client(self, connection_file,
                                                stderr_handle,
                                                is_cython=False,
                                                is_pylab=False,
                                                is_sympy=False):
        """Create kernel manager and client."""
        # Kernel spec
        kernel_spec = self.create_kernel_spec(is_cython=is_cython,
                                              is_pylab=is_pylab,
                                              is_sympy=is_sympy)

        # Kernel manager
        try:
            kernel_manager = SpyderKernelManager(
                connection_file=connection_file,
                config=None,
                autorestart=True,
            )
        except Exception:
            error_msg = _("The error is:<br><br>"
                          "<tt>{}</tt>").format(traceback.format_exc())
            return (error_msg, None)
        kernel_manager._kernel_spec = kernel_spec

        kwargs = {}
        if os.name == 'nt':
            # avoid closing fds on win+Python 3.7
            # which prevents interrupts
            # jupyter_client > 5.2.3 will do this by default
            kwargs['close_fds'] = False
        # Catch any error generated when trying to start the kernel.
        # See spyder-ide/spyder#7302.
        try:
            kernel_manager.start_kernel(stderr=stderr_handle, **kwargs)
        except Exception:
            error_msg = _("The error is:<br><br>"
                          "<tt>{}</tt>").format(traceback.format_exc())
            return (error_msg, None)

        # Kernel client
        kernel_client = kernel_manager.client()

        # Increase time to detect if a kernel is alive.
        # See spyder-ide/spyder#3444.
        kernel_client.hb_channel.time_to_dead = 18.0

        return kernel_manager, kernel_client