def load_config(module, commands, commit=False, comment=None):
    connection = get_connection(module)

    out = connection.edit_config(commands)

    diff = None
    if module._diff:
        out = connection.get('compare')
        out = to_text(out, errors='surrogate_or_strict')

        if not out.startswith('No changes'):
            out = connection.get('show')
            diff = to_text(out, errors='surrogate_or_strict').strip()

    if commit:
        try:
            out = connection.commit(comment)
        except:
            connection.discard_changes()
            module.fail_json(msg='commit failed: %s' % out)

    if not commit:
        connection.discard_changes()
    else:
        connection.get('exit')

    if diff:
        return diff