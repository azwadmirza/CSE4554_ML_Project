def add_message_event(proto_message, span, message_event_type, message_id=1):
    """Adds a MessageEvent to the span based off of the given protobuf
    message
    """
    span.add_message_event(
        time_event.MessageEvent(
            datetime.utcnow(),
            message_id,
            type=message_event_type,
            uncompressed_size_bytes=proto_message.ByteSize()
        )
    )