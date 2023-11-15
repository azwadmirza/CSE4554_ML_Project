def validate_options(options):
    """
    Ensures that the plugin options are valid.
    :param options:
    :return:
    """
    interval = get_plugin_option('interval', options)
    unit = get_plugin_option('unit', options)

    if not interval and not unit:
        return

    if unit == 'month':
        interval *= 30

    elif unit == 'week':
        interval *= 7

    if interval > 90:
        raise ValidationError('Notification cannot be more than 90 days into the future.')