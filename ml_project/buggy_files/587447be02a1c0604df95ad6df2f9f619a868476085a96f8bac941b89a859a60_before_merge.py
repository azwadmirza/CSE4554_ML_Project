    def apply(self, args=(), kwargs={}, **options):
        last, fargs = None, args
        for task in self.tasks:
            res = task.clone(fargs).apply(
                last and (last.get(),), **dict(self.options, **options))
            res.parent, last, fargs = last, res, None
        return last