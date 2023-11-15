    def create_kernel_manager_and_kernel_client(self, connection_file,
                                                stderr_file):
        """Create kernel manager and client."""
        # Kernel manager
        kernel_manager = QtKernelManager(connection_file=connection_file,
                                         config=None, autorestart=True)
        kernel_manager._kernel_spec = self.create_kernel_spec()

        # Save stderr in a file to read it later in case of errors
        if not self.testing:
            stderr = codecs.open(stderr_file, 'w', encoding='utf-8')
            kernel_manager.start_kernel(stderr=stderr)
        else:
            kernel_manager.start_kernel()

        # Kernel client
        kernel_client = kernel_manager.client()

        # Increase time to detect if a kernel is alive
        # See Issue 3444
        kernel_client.hb_channel.time_to_dead = 6.0

        return kernel_manager, kernel_client