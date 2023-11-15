        def wrapper(self, *args, **kwargs):
            if self.rule.workflow.iocache.active:
                cache = getattr(self.rule.workflow.iocache, func.__name__)
                normalized = self.rstrip("/")
                if normalized in cache:
                    return cache[normalized]
                v = func(self, *args, **kwargs)
                cache[normalized] = v
                return v
            else:
                return func(self, *args, **kwargs)