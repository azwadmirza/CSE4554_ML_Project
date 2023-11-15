    def is_encrypted(self, data):
        """ Test if this is vault encrypted data

        :arg data: a byte str or unicode string to test whether it is
            recognized as vault encrypted data
        :returns: True if it is recognized.  Otherwise, False.
        """

        if hasattr(data, 'read'):
            current_position = data.tell()
            header_part = data.read(len(b_HEADER))
            data.seek(current_position)
            return self.is_encrypted(header_part)

        if to_bytes(data, errors='strict', encoding='utf-8').startswith(b_HEADER):
            return True
        return False