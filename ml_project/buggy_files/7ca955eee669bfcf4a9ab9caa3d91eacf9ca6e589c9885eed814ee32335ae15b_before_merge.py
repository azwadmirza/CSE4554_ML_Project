    def __init__(self, address):
        """ Initializes a new instance

        :param address: The address to start reading from
        """
        ReadCoilsRequest.__init__(self, address, 16)