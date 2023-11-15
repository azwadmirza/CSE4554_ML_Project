    def __call__(self, msg=None):
        if not self.acked:
            self.acked = True
            if msg is None:
                self.q.put(self.obj)
            else:
                self.q.put(msg)