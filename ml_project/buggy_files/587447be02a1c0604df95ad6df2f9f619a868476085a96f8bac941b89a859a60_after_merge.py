    def apply(self, args=(), kwargs={}, **options):
        last, (fargs, fkwargs) = None, (args, kwargs)
        for task in self.tasks:
            res = task.clone(fargs, fkwargs).apply(
                last and (last.get(),), **dict(self.options, **options))
            res.parent, last, (fargs, fkwargs) = last, res, (None, None)
        return last