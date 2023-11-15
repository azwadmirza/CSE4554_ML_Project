    def write_register(self, address, value, **kwargs):
        """
        Write `value` to register at `address`.

        :param address: register offset to write to
        :param value: register value to write
        :param unit: The slave unit this request is targeting
        :return:
        """
        resp = super(ExtendedRequestSupport, self).write_register(
            address, value, **kwargs)
        return resp