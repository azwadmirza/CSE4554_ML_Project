    def init_kernel(self):
        """Create the Kernel object itself"""
        shell_stream = ZMQStream(self.shell_socket)
        control_stream = ZMQStream(self.control_socket)
        
        kernel_factory = import_item(str(self.kernel_class))

        kernel = kernel_factory(parent=self, session=self.session,
                                shell_streams=[shell_stream, control_stream],
                                iopub_socket=self.iopub_socket,
                                stdin_socket=self.stdin_socket,
                                log=self.log,
                                profile_dir=self.profile_dir,
                                user_ns=self.user_ns,
        )
        kernel.record_ports(self.ports)
        self.kernel = kernel