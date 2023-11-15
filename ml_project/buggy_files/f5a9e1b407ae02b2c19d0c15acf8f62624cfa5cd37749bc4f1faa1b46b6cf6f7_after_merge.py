def get_identity_notifications(connection, module, identity, retries=0, retryDelay=10):
    # Unpredictably get_identity_notifications doesn't include the notifications when we've
    # just registered the identity.
    # Don't want this complexity exposed users of the module as they'd have to retry to ensure
    # a consistent return from the module.
    # To avoid this we have an internal retry that we use only when getting the current notification
    # status for return.
    for attempt in range(0, retries + 1):
        response = call_and_handle_errors(module, connection.get_identity_notification_attributes, Identities=[identity])
        notification_attributes = response['NotificationAttributes']

        # No clear AWS docs on when this happens, but it appears sometimes identities are not included in
        # in the notification attributes when the identity is first registered. Suspect that this is caused by
        # eventual consistency within the AWS services. It's been observed in builds so we need to handle it.
        #
        # When this occurs, just return None and we'll assume no identity notification settings have been changed
        # from the default which is reasonable if this is just eventual consistency on creation.
        # See: https://github.com/ansible/ansible/issues/36065
        if identity in notification_attributes:
            break
        else:
            # Paranoia check for coding errors, we only requested one identity, so if we get a different one
            # something has gone very wrong.
            if len(notification_attributes) != 0:
                module.fail_json(
                    msg='Unexpected identity found in notification attributes, expected {0} but got {1!r}.'.format(
                        identity,
                        notification_attributes.keys(),
                    )
                )
        time.sleep(retryDelay)
    if identity not in notification_attributes:
        return None
    return notification_attributes[identity]