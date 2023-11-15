    def _is_packed_binary(self, data):
        '''
        Check if data is hexadecimal packed

        :param data:
        :return:
        '''
        packed = False
        if len(data) == 16 and ':' not in data:
            try:
                packed = bool(int(str(bytearray(data)).encode('hex'), 16))
            except ValueError:
                pass

        return packed