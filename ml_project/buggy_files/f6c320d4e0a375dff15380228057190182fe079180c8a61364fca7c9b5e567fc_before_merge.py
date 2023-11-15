    def execute(self, context=None):
        ''' Run a read exeception status request against the store

        :returns: The populated response
        '''
        identifier = b'Pymodbus'
        return ReportSlaveIdResponse(identifier)