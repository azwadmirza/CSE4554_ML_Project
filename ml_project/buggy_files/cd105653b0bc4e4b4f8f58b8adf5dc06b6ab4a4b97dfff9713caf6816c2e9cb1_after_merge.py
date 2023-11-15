    def _ir_calibrate(self, data):
        """Calibrate IR channels to BT."""
        fk1 = float(self.nc["planck_fk1"])
        fk2 = float(self.nc["planck_fk2"])
        bc1 = float(self.nc["planck_bc1"])
        bc2 = float(self.nc["planck_bc2"])

        res = (fk2 / xu.log(fk1 / data + 1) - bc1) / bc2
        res.attrs = data.attrs
        res.attrs['units'] = 'K'

        return res