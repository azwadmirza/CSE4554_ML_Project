    def execute(self, context=None):
        ''' Run a read exeception status request against the store

        :returns: The populated response
        '''
        information = DeviceInformationFactory.get(_MCB)
        identifier = "-".join(information.values()).encode()
        identifier = identifier or b'Pymodbus'
        return ReportSlaveIdResponse(identifier)