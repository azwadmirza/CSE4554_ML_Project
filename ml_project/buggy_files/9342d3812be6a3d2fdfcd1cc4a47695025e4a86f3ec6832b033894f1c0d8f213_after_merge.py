    def _get_call_return_value(self, call_dict, call_data, comm_id):
        """
        Interupt the kernel if needed.
        """
        settings = call_dict['settings']
        blocking = 'blocking' in settings and settings['blocking']

        if not self.kernel_client.is_alive():
            if blocking:
                raise RuntimeError("Kernel is dead")
            else:
                # The user has other problems
                return

        settings = call_dict['settings']
        interrupt = 'interrupt' in settings and settings['interrupt']

        try:
            with self.comm_channel_manager(
                    comm_id, queue_message=not interrupt):
                return super(KernelComm, self)._get_call_return_value(
                    call_dict, call_data, comm_id)
        except RuntimeError:
            if blocking:
                raise
            else:
                # The user has other problems
                return