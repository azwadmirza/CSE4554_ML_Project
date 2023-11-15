    def clear(self, *args, **kwargs):
        super(tqdm_telegram, self).clear(*args, **kwargs)
        if not self.disable:
            self.tgio.write("")