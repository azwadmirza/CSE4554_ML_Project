    def _get_call_return_value(self, call_dict, call_data, comm_id):
        """
        Interupt the kernel if needed.
        """
        settings = call_dict['settings']
        interrupt = 'interrupt' in settings and settings['interrupt']

        with self.comm_channel_manager(comm_id, queue_message=not interrupt):
            return super(KernelComm, self)._get_call_return_value(
                call_dict, call_data, comm_id)