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

    if interval == 'month':
        unit *= 30

    elif interval == 'week':
        unit *= 7

    if unit > 90:
        raise ValidationError('Notification cannot be more than 90 days into the future.')