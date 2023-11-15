    def _ir_calibrate(self, data):
        """Calibrate IR channels to BT."""
        fk1 = self.nc["planck_fk1"][()]
        fk2 = self.nc["planck_fk2"][()]
        bc1 = self.nc["planck_bc1"][()]
        bc2 = self.nc["planck_bc2"][()]

        np.divide(fk1, data, out=data.data)
        data.data[:] += 1
        np.log(data, out=data.data)
        np.divide(fk2, data, out=data.data)
        data.data[:] -= bc1
        data.data[:] /= bc2

        return 'K'