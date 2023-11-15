def update_feedback_forwarding(connection, module, identity, identity_notifications):
    if identity_notifications is None:
        # AWS requires feedback forwarding to be enabled unless bounces and complaints
        # are being handled by SNS topics. So in the absence of identity_notifications
        # information existing feedback forwarding must be on.
        current = True
    elif 'ForwardingEnabled' in identity_notifications:
        current = identity_notifications['ForwardingEnabled']
    else:
        # If there is information on the notifications setup but no information on the
        # forwarding state it's pretty safe to assume forwarding is off. AWS API docs
        # suggest this information will always be included but best to be defensive
        current = False

    required = module.params.get('feedback_forwarding')

    if current != required:
        call_and_handle_errors(
            module,
            connection.set_identity_feedback_forwarding_enabled,
            Identity=identity,
            ForwardingEnabled=required,
        )
        return True
    return False