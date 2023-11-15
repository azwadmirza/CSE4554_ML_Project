def update_notification_topic_headers(connection, module, identity, identity_notifications, notification_type):
    arg_dict = module.params.get(notification_type.lower() + '_notifications')
    header_key = 'HeadersIn' + notification_type + 'NotificationsEnabled'
    if identity_notifications is None:
        # If there is no configuration for topic notifications, headers cannot be being
        # forwarded, hence assume false.
        current = False
    elif header_key in identity_notifications:
        current = identity_notifications[header_key]
    else:
        # AWS API doc indicates that the headers in fields are optional. Unfortunately
        # it's not clear on what this means. But it's a pretty safe assumption that it means
        # headers are not included since most API consumers would interpret absence as false.
        current = False

    if arg_dict is not None and 'include_headers' in arg_dict:
        required = arg_dict['include_headers']
    else:
        required = False

    if current != required:
        call_and_handle_errors(
            module,
            connection.set_identity_headers_in_notifications_enabled,
            Identity=identity,
            NotificationType=notification_type,
            Enabled=required,
        )
        return True
    return False