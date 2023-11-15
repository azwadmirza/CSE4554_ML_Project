    def setValues(self, fx, address, values):
        ''' Sets the datastore with the supplied values

        :param fx: The function we are working with
        :param address: The starting address
        :param values: The new values to be set
        '''
        address = address + 1  # section 4.4 of specification
        _logger.debug("set-values[%d] %d:%d" % (fx, address, len(values)))
        self._set(self.decode(fx), address, values)