    def __getattr__(self, k):
        return getattr(self.original_reply, k)