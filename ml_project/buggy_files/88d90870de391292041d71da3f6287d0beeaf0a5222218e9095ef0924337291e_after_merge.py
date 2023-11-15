def _receive_messages(
    sock: ssl.SSLSocket,
    sock_receive_lock: Lock,
    logger: Logger,
    receive_buffer_size: int = 1024,
    all_message_trace_enabled: bool = False,
) -> List[Tuple[Optional[FrameHeader], bytes]]:
    def receive(specific_buffer_size: Optional[int] = None):
        size = (
            specific_buffer_size
            if specific_buffer_size is not None
            else receive_buffer_size
        )
        with sock_receive_lock:
            try:
                received_bytes = sock.recv(size)
                if all_message_trace_enabled:
                    if len(received_bytes) > 0:
                        logger.debug(f"Received bytes: {received_bytes}")
                return received_bytes
            except OSError as e:
                if e.errno == errno.EBADF:
                    logger.debug("The connection seems to be already closed.")
                    return bytes()
                raise e

    return _fetch_messages(
        messages=[],
        receive=receive,
        remaining_bytes=None,
        current_mask_key=None,
        current_header=None,
        current_data=bytes(),
        logger=logger,
    )