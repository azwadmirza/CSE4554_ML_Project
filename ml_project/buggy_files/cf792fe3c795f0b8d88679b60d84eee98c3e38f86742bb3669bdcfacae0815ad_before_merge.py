    def __init__(self, address):
        ModbusRequest.__init__(self)
        self.address = address
        self.count = 16