def master(master=None, connected=True):
    '''
    .. versionadded:: 2014.7.0

    Return the connection status with master. Fire an event if the
    connection to master is not as expected. This function is meant to be
    run via a scheduled job from the minion. If master_ip is an FQDN/Hostname,
    it must be resolvable to a valid IPv4 address.

    CLI Example:

    .. code-block:: bash

        salt '*' status.master
    '''
    master_ips = None

    if master:
        master_ips = _host_to_ips(master)

    if not master_ips:
        return

    master_connection_status = False
    connected_ips = _connected_masters()

    # Get connection status for master
    for master_ip in master_ips:
        if master_ip in connected_ips:
            master_connection_status = True
            break

    # Connection to master is not as expected
    if master_connection_status is not connected:
        event = salt.utils.event.get_event('minion', opts=__opts__, listen=False)
        if master_connection_status:
            event.fire_event({'master': master}, salt.minion.master_event(type='connected'))
        else:
            event.fire_event({'master': master}, salt.minion.master_event(type='disconnected'))

    return master_connection_status