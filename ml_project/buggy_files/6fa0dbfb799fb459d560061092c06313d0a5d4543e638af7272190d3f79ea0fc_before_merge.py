def missedmessage_hook(user_profile_id, queue, last_for_client):
    # type: (int, ClientDescriptor, bool) -> None
    # Only process missedmessage hook when the last queue for a
    # client has been garbage collected
    if not last_for_client:
        return

    message_ids_to_notify = []  # type: List[Dict[str, Any]]
    for event in queue.event_queue.contents():
        if event['type'] != 'message':
            continue
        assert 'flags' in event

        flags = event['flags']
        mentioned = 'mentioned' in flags and 'read' not in flags
        if mentioned:
            notify_info = dict(message_id=event['message']['id'])

            if not event.get('push_notified', False):
                notify_info['send_push'] = True
            if not event.get('email_notified', False):
                notify_info['send_email'] = True
            message_ids_to_notify.append(notify_info)

    for notify_info in message_ids_to_notify:
        msg_id = notify_info['message_id']
        notice = build_offline_notification(user_profile_id, msg_id)
        if notify_info.get('send_push', False):
            queue_json_publish("missedmessage_mobile_notifications", notice, lambda notice: None)
        if notify_info.get('send_email', False):
            queue_json_publish("missedmessage_emails", notice, lambda notice: None)