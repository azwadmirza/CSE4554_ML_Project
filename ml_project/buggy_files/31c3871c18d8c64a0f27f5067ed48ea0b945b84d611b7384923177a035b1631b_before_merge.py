    def convert(self, value, view):
        if not isinstance(value, self.typ):
            self.fail(
                'must be a {0}, not {1}'.format(
                    self.typ.__name__,
                    type(value).__name__,
                ),
                view,
                True
            )
        return value