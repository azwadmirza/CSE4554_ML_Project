    def __call__(self, msg=NO_REPLY):
        if not self.acked:
            self.acked = True
            if msg is NO_REPLY:
                self.q.put(self.obj)
            else:
                self.q.put(msg)