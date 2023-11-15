    def get_network_status_monitor(cls) -> 'NetworkStatusMonitor':
        if sys.platform == 'darwin':
            from .darwin import DarwinNetworkStatus
            return DarwinNetworkStatus()
        else:
            from .network_manager import NetworkManagerMonitor, UnsupportedException, DBusException
            try:
                return NetworkManagerMonitor()
            except (UnsupportedException, DBusException):
                return NullNetworkStatusMonitor()