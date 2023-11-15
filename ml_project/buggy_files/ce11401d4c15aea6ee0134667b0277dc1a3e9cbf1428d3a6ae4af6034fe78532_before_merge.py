    def receive(specific_buffer_size: Optional[int] = None):
        size = (
            specific_buffer_size
            if specific_buffer_size is not None
            else receive_buffer_size
        )
        received_bytes = sock.recv(size)
        if all_message_trace_enabled:
            if len(received_bytes) > 0:
                logger.debug(f"Received bytes: {received_bytes}")
        return received_bytes