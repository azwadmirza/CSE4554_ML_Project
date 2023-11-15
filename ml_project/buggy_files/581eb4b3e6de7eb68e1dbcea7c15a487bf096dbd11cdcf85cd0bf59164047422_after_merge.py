    def unicode_char_to_hex(uchr):
        # Covert a unicode char to hex string, without prefix
        if len(uchr) == 1 and ord(uchr) < 128:
            return format(ord(uchr), 'x')
        return (uchr.encode('unicode-escape').decode('utf-8')
            .lstrip('\\U').lstrip('\\u').lstrip('\\x').lstrip('0'))