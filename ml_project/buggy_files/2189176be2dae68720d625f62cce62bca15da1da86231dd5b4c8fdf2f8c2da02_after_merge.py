    def generate(self):
        """Generate items."""
        for c, inp, site, args, kwargs in self._items:
            if c:
                if site:
                    kwargs['site'] = self.site
                    kwargs['context'] = self.context
                yield inp(*args, **kwargs)
            else:
                yield inp