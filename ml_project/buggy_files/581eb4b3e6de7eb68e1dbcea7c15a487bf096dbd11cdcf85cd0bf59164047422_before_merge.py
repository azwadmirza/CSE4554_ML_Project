    def unicode_char_to_hex(uchr):
        # Covert a unicode char to hex string, without prefix
        return uchr.encode('unicode-escape').decode('utf-8').lstrip('\\U').lstrip('\\u').lstrip('0')