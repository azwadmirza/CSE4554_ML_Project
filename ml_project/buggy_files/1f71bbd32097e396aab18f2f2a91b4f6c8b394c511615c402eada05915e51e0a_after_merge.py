def list_(name=None, runas=None):
    '''
    Run launchctl list and return the output

    :param str name: The name of the service to list

    :param str runas: User to run launchctl commands

    :return: If a name is passed returns information about the named service,
        otherwise returns a list of all services and pids
    :rtype: str

    CLI Example:

    .. code-block:: bash

        salt '*' service.list
        salt '*' service.list org.cups.cupsd
    '''
    if name:
        # Get service information and label
        service = _get_service(name)
        label = service['plist']['Label']

        # Collect information on service: will raise an error if it fails
        return launchctl('list',
                         label,
                         return_stdout=True,
                         runas=runas)

    # Collect information on all services: will raise an error if it fails
    return launchctl('list',
                     return_stdout=True,
                     runas=runas)