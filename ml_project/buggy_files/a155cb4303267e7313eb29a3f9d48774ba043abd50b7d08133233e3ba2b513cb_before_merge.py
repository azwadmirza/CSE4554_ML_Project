    def create_kernel_manager_and_kernel_client(self, connection_file,
                                                stderr_file,
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
            kernel_manager = QtKernelManager(connection_file=connection_file,
                                             config=None, autorestart=True)
        except Exception:
            error_msg = _("The error is:<br><br>"
                          "<tt>{}</tt>").format(traceback.format_exc())
            return (error_msg, None)
        kernel_manager._kernel_spec = kernel_spec

        # Save stderr in a file to read it later in case of errors
        if stderr_file is not None:
            # Needed to prevent any error that could appear.
            # See issue 6267
            try:
                stderr = codecs.open(stderr_file, 'w', encoding='utf-8')
            except Exception:
                stderr = None
        else:
            stderr = None
        kernel_manager.start_kernel(stderr=stderr)

        # Kernel client
        kernel_client = kernel_manager.client()

        # Increase time to detect if a kernel is alive
        # See Issue 3444
        kernel_client.hb_channel.time_to_dead = 18.0

        return kernel_manager, kernel_client