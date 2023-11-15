def missedmessage_hook(user_profile_id, queue, last_for_client):
    # type: (int, ClientDescriptor, bool) -> None
    # Only process missedmessage hook when the last queue for a
    # client has been garbage collected
    if not last_for_client:
        return

    for event in queue.event_queue.contents():
        if event['type'] != 'message':
            continue
        assert 'flags' in event

        flags = event['flags']
        mentioned = 'mentioned' in flags and 'read' not in flags
        # TODO: These next variables should be extracted from the
        # event, but to match the historical effect of this function
        # in only supporting mentions, we've just hardcoded them to
        # False.  Fixing this will correct currently buggy behavior in
        # our handling of private message and users who've requested
        # stream push notifications.
        private_message = False
        stream_push_notify = False
        stream_name = None
        always_push_notify = False
        # Since we just GC'd the last event queue, the user is definitely idle.
        idle = True

        message_id = event['message']['id']
        maybe_enqueue_notifications(user_profile_id, message_id, private_message, mentioned,
                                    stream_push_notify, stream_name, always_push_notify, idle)