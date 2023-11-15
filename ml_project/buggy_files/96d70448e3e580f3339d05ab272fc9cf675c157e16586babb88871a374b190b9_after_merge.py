    def __call__(self, data):
        self.randomize()
        d = dict(data)
        if not self._do_transform:
            return d
        rotator = Rotate(
            angle=self.x if d[self.keys[0]].ndim == 3 else (self.x, self.y, self.z), keep_size=self.keep_size,
        )
        for idx, key in enumerate(self.keys):
            d[key] = rotator(
                d[key],
                mode=self.mode[idx],
                padding_mode=self.padding_mode[idx],
                align_corners=self.align_corners[idx],
                dtype=self.dtype[idx],
            )
        return d