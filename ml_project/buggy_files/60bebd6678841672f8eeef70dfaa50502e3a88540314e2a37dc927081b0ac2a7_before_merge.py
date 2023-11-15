def get_format(format=None):
    """Return the command tempate and the extension from the config.
    """
    if not format:
        format = config['convert']['format'].get(unicode).lower()
    format = ALIASES.get(format, format)

    try:
        format_info = config['convert']['formats'][format].get(dict)
        command = format_info['command']
        extension = format_info['extension']
    except KeyError:
        raise ui.UserError(
            u'convert: format {0} needs "command" and "extension" fields'
            .format(format)
        )
    except ConfigTypeError:
        command = config['convert']['formats'][format].get(bytes)
        extension = format

    # Convenience and backwards-compatibility shortcuts.
    keys = config['convert'].keys()
    if 'command' in keys:
        command = config['convert']['command'].get(unicode)
    elif 'opts' in keys:
        # Undocumented option for backwards compatibility with < 1.3.1.
        command = u'ffmpeg -i $source -y {0} $dest'.format(
            config['convert']['opts'].get(unicode)
        )
    if 'extension' in keys:
        extension = config['convert']['extension'].get(unicode)

    return (command.encode('utf8'), extension.encode('utf8'))