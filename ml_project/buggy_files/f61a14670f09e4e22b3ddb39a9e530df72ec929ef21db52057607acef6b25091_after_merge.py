    def repr(self):
        return dict(
            [(k, v) for k, v in self._asdict().items() if v is not None]
        )