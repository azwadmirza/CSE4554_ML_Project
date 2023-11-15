    def clear(self, *args, **kwargs):
        super(tqdm_discord, self).clear(*args, **kwargs)
        self.dio.write("")