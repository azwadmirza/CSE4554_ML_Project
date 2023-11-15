    def write_coil(self, address, value, **kwargs):
        """
        Write `value` to coil at `address`.

        :param address: coil offset to write to
        :param value: bit value to write
        :param unit: The slave unit this request is targeting
        :return:
        """
        resp = super(ExtendedRequestSupport, self).write_coil(
            address, value, **kwargs)
        if not resp.isError():
            return {
                'function_code': resp.function_code,
                'address': resp.address,
                'value': resp.value
            }
        else:
            return ExtendedRequestSupport._process_exception(resp)