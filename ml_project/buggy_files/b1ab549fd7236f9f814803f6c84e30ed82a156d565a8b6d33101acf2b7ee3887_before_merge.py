    def _helper(self, data):
        '''
        This factory is used to generate the correct request object
        from a valid request packet. This decodes from a list of the
        currently implemented request types.

        :param data: The request packet to decode
        :returns: The decoded request or illegal function request object
        '''
        function_code = byte2int(data[0])
        _logger.debug("Factory Request[%d]" % function_code)
        request = self.__lookup.get(function_code, lambda: None)()
        if not request:
            request = IllegalFunctionRequest(function_code)
        request.decode(data[1:])

        if hasattr(request, 'sub_function_code'):
            lookup = self.__sub_lookup.get(request.function_code, {})
            subtype = lookup.get(request.sub_function_code, None)
            if subtype: request.__class__ = subtype

        return request