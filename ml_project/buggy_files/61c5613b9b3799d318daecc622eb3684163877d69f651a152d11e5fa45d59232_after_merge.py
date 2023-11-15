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
                logger.info(
                    "Dropping message because kernel is dead: ",
                    str(call_dict)
                )
                return

        settings = call_dict['settings']
        interrupt = 'interrupt' in settings and settings['interrupt']
        interrupt = interrupt or blocking
        # Need to make sure any blocking call is replied rapidly.
        if interrupt and not self.comm_channel_connected():
            # Ask again for comm config
            self.remote_call()._send_comm_config()
            # Can not interrupt if comm not connected
            interrupt = False
            logger.debug(
                "Dropping interrupt because comm is disconnected: " +
                str(call_dict)
            )
            if blocking:
                raise CommError("Cannot block on a disconnected comm")
        try:
            with self.comm_channel_manager(
                    comm_id, queue_message=not interrupt):
                return super(KernelComm, self)._get_call_return_value(
                    call_dict, call_data, comm_id)
        except RuntimeError as e:
            if blocking:
                raise
            else:
                # The user has other problems
                logger.info(
                    "Dropping message because of exception: ",
                    str(e),
                    str(call_dict)
                )
                return