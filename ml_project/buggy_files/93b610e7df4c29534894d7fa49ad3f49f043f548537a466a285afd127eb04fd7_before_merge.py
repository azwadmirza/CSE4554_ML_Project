    def clear(self, *args, **kwargs):
        super(tqdm_telegram, self).clear(*args, **kwargs)
        self.tgio.write("")