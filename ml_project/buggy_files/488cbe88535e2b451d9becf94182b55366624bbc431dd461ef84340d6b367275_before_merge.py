    def signal1D(self, value):
        if isinstance(value, EELSSpectrum):
            self._signal = value
            self.signal._are_microscope_parameters_missing()
        else:
            raise ValueError(
                "This attribute can only contain an EELSSpectrum "
                "but an object of type %s was provided" %
                str(type(value)))