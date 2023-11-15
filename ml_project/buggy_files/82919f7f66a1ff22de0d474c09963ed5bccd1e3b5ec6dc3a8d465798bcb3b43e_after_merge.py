def get_all(runas=None):
    '''
    Return a list of services that are enabled or available. Can be used to
    find the name of a service.

    :param str runas: User to run launchctl commands

    :return: A list of all the services available or enabled
    :rtype: list

    CLI Example:

    .. code-block:: bash

        salt '*' service.get_all
    '''
    # Get list of enabled services
    enabled = get_enabled(runas=runas)

    # Get list of all services
    available = list(__utils__['mac_utils.available_services']().keys())

    # Return composite list
    return sorted(set(enabled + available))