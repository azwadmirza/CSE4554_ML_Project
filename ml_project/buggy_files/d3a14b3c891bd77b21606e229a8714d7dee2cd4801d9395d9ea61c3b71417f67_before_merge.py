    def __init__(self, address, bus):
        super(TSL2591Sensor, self).__init__()
        self.logger = logging.getLogger(
            "mycodo.sensors.tsl2591_{bus}_{add}".format(bus=bus, add=address))
        self.i2c_address = address
        self.i2c_bus = bus
        self._lux = 0.0