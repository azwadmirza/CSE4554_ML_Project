    def __init__(self, address=None, **kwargs):
        ModbusRequest.__init__(self, **kwargs)
        self.address = address
        self.count = 16