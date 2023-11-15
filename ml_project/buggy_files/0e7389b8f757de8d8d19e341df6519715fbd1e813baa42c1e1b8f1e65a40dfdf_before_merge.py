    def __call__(self, data):
        d = dict(data)
        for idx, key in enumerate(self.keys):
            d[key] = self.rotator(
                d[key], mode=self.mode[idx], padding_mode=self.padding_mode[idx], align_corners=self.align_corners[idx],
            )
        return d