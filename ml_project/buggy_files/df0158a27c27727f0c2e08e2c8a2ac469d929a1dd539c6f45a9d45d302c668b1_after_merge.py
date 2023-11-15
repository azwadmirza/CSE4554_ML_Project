    def makePickle(self, record):
        return salt.utils.stringutils.to_bytes(self.format(record))