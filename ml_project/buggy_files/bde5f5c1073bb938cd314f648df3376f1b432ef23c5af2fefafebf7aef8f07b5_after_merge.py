def _handle_error(remaining_retries, command, return_tuple, no_log, host, display=display):

    # sshpass errors
    if command == b'sshpass':
        # Error 5 is invalid/incorrect password. Raise an exception to prevent retries from locking the account.
        if return_tuple[0] == 5:
            msg = 'Invalid/incorrect username/password. Skipping remaining {0} retries to prevent account lockout:'.format(remaining_retries)
            if remaining_retries <= 0:
                msg = 'Invalid/incorrect password:'
            if no_log:
                msg = '{0} <error censored due to no log>'.format(msg)
            else:
                msg = '{0} {1}'.format(msg, to_native(return_tuple[2]).rstrip())
            raise AnsibleAuthenticationFailure(msg)

        # sshpass returns codes are 1-6. We handle 5 previously, so this catches other scenarios.
        # No exception is raised, so the connection is retried.
        elif return_tuple[0] in [1, 2, 3, 4, 6]:
            msg = 'sshpass error:'
            if no_log:
                msg = '{0} <error censored due to no log>'.format(msg)
            else:
                msg = '{0} {1}'.format(msg, to_native(return_tuple[2]).rstrip())

    if return_tuple[0] == 255:
        SSH_ERROR = True
        for signature in b_NOT_SSH_ERRORS:
            if signature in return_tuple[1]:
                SSH_ERROR = False
                break

        if SSH_ERROR:
            msg = "Failed to connect to the host via ssh:"
            if no_log:
                msg = '{0} <error censored due to no log>'.format(msg)
            else:
                msg = '{0} {1}'.format(msg, to_native(return_tuple[2]).rstrip())
            raise AnsibleConnectionFailure(msg)

    # For other errors, no execption is raised so the connection is retried and we only log the messages
    if 1 <= return_tuple[0] <= 254:
        msg = u"Failed to connect to the host via ssh:"
        if no_log:
            msg = u'{0} <error censored due to no log>'.format(msg)
        else:
            msg = u'{0} {1}'.format(msg, to_text(return_tuple[2]).rstrip())
        display.vvv(msg, host=host)