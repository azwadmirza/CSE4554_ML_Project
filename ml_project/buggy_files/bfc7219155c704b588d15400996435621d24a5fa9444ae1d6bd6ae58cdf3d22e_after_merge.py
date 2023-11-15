def win_interfaces():
    '''
    Obtain interface information for Windows systems
    '''
    return salt.utils.win_network.get_interface_info()