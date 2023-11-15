    def get_network_status_monitor(cls) -> 'NetworkStatusMonitor':
        if sys.platform == 'darwin':
            from .darwin import DarwinNetworkStatus
            return DarwinNetworkStatus()
        else:
            from .network_manager import NetworkManagerMonitor, UnsupportedException
            try:
                return NetworkManagerMonitor()
            except UnsupportedException:
                return NullNetworkStatusMonitor()