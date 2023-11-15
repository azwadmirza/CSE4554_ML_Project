    def __getattr__(self, k):
        return getattr(self.reply_func, k)