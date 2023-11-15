    def __init__(self, string=""):
        """ Initialize the exception

        :param string: The message to append to the error
        """
        message = "[Invalid Parameter] %s" % string
        ModbusException.__init__(self, message)