    def get_measurement(self):
        """ Gets the TSL2591's lux """
        tsl = tsl2591.Tsl2591(i2c_bus=self.i2c_bus, sensor_address=self.i2c_address)
        full, ir = tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
        lux = tsl.calculate_lux(full, ir)  # convert raw values to lux
        return lux