    def apply_async(self, args=(), kwargs={}, task_id=None,
                    producer=None, publisher=None, connection=None,
                    router=None, result_cls=None, **options):
        kwargs = kwargs or {}
        args = (tuple(args) + tuple(self.args)
                if args and not self.immutable else self.args)
        body = kwargs.pop('body', None) or self.kwargs['body']
        kwargs = dict(self.kwargs['kwargs'], **kwargs)
        body = body.clone(**options)
        app = self._get_app(body)
        tasks = (self.tasks.clone() if isinstance(self.tasks, group)
                 else group(self.tasks, app=app))
        if app.conf.task_always_eager:
            return self.apply(args, kwargs,
                              body=body, task_id=task_id, **options)
        # chord([A, B, ...], C)
        return self.run(tasks, body, args, task_id=task_id, **options)