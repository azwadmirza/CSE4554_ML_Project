def update_notification_topic(connection, module, identity, identity_notifications, notification_type):
    arg_dict = module.params.get(notification_type.lower() + '_notifications')
    topic_key = notification_type + 'Topic'
    if identity_notifications is None:
        # If there is no configuration for notifications cannot be being sent to topics
        # hence assume None as the current state.
        current = None
    elif topic_key in identity_notifications:
        current = identity_notifications[topic_key]
    else:
        # If there is information on the notifications setup but no information on the
        # particular notification topic it's pretty safe to assume there's no topic for
        # this notification. AWS API docs suggest this information will always be
        # included but best to be defensive
        current = None

    if arg_dict is not None and 'topic' in arg_dict:
        required = arg_dict['topic']
    else:
        required = None

    if current != required:
        call_and_handle_errors(
            module,
            connection.set_identity_notification_topic,
            Identity=identity,
            NotificationType=notification_type,
            SnsTopic=required,
        )
        return True
    return False