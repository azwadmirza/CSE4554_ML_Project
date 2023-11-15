    def signal1D(self, value):
        if isinstance(value, EELSSpectrum):
            self._signal = value
            if self.signal._are_microscope_parameters_missing():
                raise ValueError(
                    "The required microscope parameters are not defined in "
                    "the EELS spectrum signal metadata. Use "
                    "``set_microscope_parameters`` to set them."
                )
        else:
            raise ValueError(
                "This attribute can only contain an EELSSpectrum "
                "but an object of type %s was provided" %
                str(type(value)))