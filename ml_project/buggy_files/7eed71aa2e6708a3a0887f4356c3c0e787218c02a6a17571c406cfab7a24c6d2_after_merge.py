    def get_measurement(self):
        """ Gets the TSL2591's lux """
        full, ir = self.tsl.get_full_luminosity()  # read raw values (full spectrum and ir spectrum)
        lux = self.tsl.calculate_lux(full, ir)  # convert raw values to lux
        return lux