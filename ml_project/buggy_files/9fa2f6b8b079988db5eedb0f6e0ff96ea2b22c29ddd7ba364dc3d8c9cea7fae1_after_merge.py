    def write(self, msg):
        self.msg += msg
        if self.msg[-1] == '\n':
            self.queue.append(self.msg)
            self.msg = ''