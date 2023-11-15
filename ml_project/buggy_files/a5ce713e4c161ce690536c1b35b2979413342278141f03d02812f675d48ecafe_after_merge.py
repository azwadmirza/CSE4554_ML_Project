    def lookupPduClass(self, function_code):
        """ Use `function_code` to determine the class of the PDU.

        :param function_code: The function code specified in a frame.
        :returns: The class of the PDU that has a matching `function_code`.
        """
        raise NotImplementedException(
            "Method not implemented by derived class")