    def __init__(self, string="", function_code=None):
        """ Initialize the exception
        :param string: The message to append to the error
        """
        self.fcode = function_code
        self.message = "[Input/Output] %s" % string
        ModbusException.__init__(self, self.message)