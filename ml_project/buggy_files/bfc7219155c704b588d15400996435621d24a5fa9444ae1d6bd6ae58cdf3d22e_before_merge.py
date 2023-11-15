def win_interfaces():
    '''
    Obtain interface information for Windows systems
    '''
    if WIN_NETWORK_LOADED is False:
        # Let's throw the ImportException again
        import salt.utils.win_network
    return salt.utils.win_network.get_interface_info()