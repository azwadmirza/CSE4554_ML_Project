def load_config(module, candidate, warnings, action='merge', commit=False, format='xml',
                comment=None, confirm=False, confirm_timeout=None):

    if not candidate:
        return

    with locked_config(module):
        if isinstance(candidate, list):
            candidate = '\n'.join(candidate)

        reply = load_configuration(module, candidate, action=action, format=format)
        if isinstance(reply, list):
            warnings.extend(reply)

        validate(module)
        diff = get_diff(module)

        if diff:
            if commit:
                commit_configuration(module, confirm=confirm, comment=comment,
                                     confirm_timeout=confirm_timeout)
            else:
                discard_changes(module)

        return diff