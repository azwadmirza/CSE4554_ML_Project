    def getValues(self, fx, address, count=1):
        ''' Get `count` values from datastore

        :param fx: The function we are working with
        :param address: The starting address
        :param count: The number of values to retrieve
        :returns: The requested values from a:a+c
        '''
        if not self.zero_mode:
            address = address + 1
        _logger.debug("getValues[%d] %d:%d" % (fx, address, count))
        return self.store[self.decode(fx)].getValues(address, count)