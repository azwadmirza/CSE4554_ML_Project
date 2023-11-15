def _get_network_interfaces():
    clr.AddReference('System.Net')
    return NetworkInformation.NetworkInterface.GetAllNetworkInterfaces()