    def create_client(self, device: 'Device',
                      handler: Optional['HardwareHandlerBase']) -> Optional['HardwareClientBase']:
        raise NotImplementedError()