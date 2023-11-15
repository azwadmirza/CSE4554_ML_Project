    def __init__(self, address, bus):
        super(TSL2591Sensor, self).__init__()
        self.logger = logging.getLogger(
            "mycodo.sensors.tsl2591_{bus}_{add}".format(bus=bus, add=address))
        self.i2c_address = address
        self.i2c_bus = bus
        self._lux = 0.0
        self.tsl = tsl2591.Tsl2591(i2c_bus=self.i2c_bus, sensor_address=self.i2c_address)