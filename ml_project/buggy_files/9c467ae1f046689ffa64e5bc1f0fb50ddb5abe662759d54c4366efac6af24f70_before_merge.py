def enabled_service_list():
    """Returns an ordered list of enabled and valid subliminal provider names

    :return: list of provider names
    :rtype: list of str
    """
    return [service['name'] for service in sorted_service_list() if service['enabled']]