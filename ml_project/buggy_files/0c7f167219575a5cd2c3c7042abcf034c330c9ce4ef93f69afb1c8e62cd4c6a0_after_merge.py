    def _is_packed_binary(self, data):
        '''
        Check if data is hexadecimal packed

        :param data:
        :return:
        '''
        packed = False
        if isinstance(data, bytes) and len(data) == 16 and b':' not in data:
            try:
                packed = bool(int(str(bytearray(data)).encode('hex'), 16))
            except ValueError:
                pass

        return packed