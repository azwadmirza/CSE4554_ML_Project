    def emit(self, record):
        formatted_object = self.format(record)
        self.publisher.send(formatted_object)