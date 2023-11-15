    def __init__(self, rdclass, rdtype, strings):
        super(TXTBase, self).__init__(rdclass, rdtype)
        if isinstance(strings, binary_type) or \
           isinstance(strings, string_types):
            strings = [strings]
        self.strings = []
        for string in strings:
            if isinstance(string, string_types):
                string = string.encode()
            self.strings.append(string)