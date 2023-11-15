    def write(self, message):
        try:
            if message == '\n':
                self.logger.debug(self.buffer)
                print(self.buffer)
                self.buffer = ''
            else:
                self.buffer += message
        except:
            pass