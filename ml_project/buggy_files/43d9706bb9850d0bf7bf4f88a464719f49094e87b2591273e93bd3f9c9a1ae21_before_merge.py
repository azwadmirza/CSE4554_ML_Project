def _get_service(name):
    '''
    Get information about a service.  If the service is not found, raise an
    error

    :param str name: Service label, file name, or full path

    :return: The service information for the service, otherwise an Error
    :rtype: dict
    '''
    services = salt.utils.mac_utils.available_services()
    name = name.lower()

    if name in services:
        # Match on label
        return services[name]

    for service in six.itervalues(services):
        if service['file_path'].lower() == name:
            # Match on full path
            return service
        basename, ext = os.path.splitext(service['file_name'])
        if basename.lower() == name:
            # Match on basename
            return service

    # Could not find service
    raise CommandExecutionError('Service not found: {0}'.format(name))