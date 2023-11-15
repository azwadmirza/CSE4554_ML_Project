    def emit(self, record):
        formatted_object = salt.utils.stringutils.to_bytes(self.format(record))
        self.publisher.send(formatted_object)