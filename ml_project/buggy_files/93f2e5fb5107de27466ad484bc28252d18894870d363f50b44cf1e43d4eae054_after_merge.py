    def to_bytes(self):
        """Serialize the DocBin's annotations to a bytestring.

        RETURNS (bytes): The serialized DocBin.

        DOCS: https://spacy.io/api/docbin#to_bytes
        """
        for tokens in self.tokens:
            assert len(tokens.shape) == 2, tokens.shape  # this should never happen
        lengths = [len(tokens) for tokens in self.tokens]
        tokens = numpy.vstack(self.tokens) if self.tokens else numpy.asarray([])
        spaces = numpy.vstack(self.spaces) if self.spaces else numpy.asarray([])

        msg = {
            "attrs": self.attrs,
            "tokens": tokens.tobytes("C"),
            "spaces": spaces.tobytes("C"),
            "lengths": numpy.asarray(lengths, dtype="int32").tobytes("C"),
            "strings": list(self.strings),
            "cats": self.cats,
        }
        if self.store_user_data:
            msg["user_data"] = self.user_data
        return zlib.compress(srsly.msgpack_dumps(msg))