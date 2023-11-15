    def _task_from_fun(self, fun, name=None, base=None, bind=False, **options):
        if not self.finalized and not self.autofinalize:
            raise RuntimeError('Contract breach: app not finalized')
        name = name or self.gen_task_name(fun.__name__, fun.__module__)
        base = base or self.Task

        if name not in self._tasks:
            run = fun if bind else staticmethod(fun)
            task = type(fun.__name__, (base,), dict({
                'app': self,
                'name': name,
                'run': run,
                '_decorated': True,
                '__doc__': fun.__doc__,
                '__module__': fun.__module__,
                '__header__': staticmethod(head_from_fun(fun, bound=bind)),
                '__wrapped__': run}, **options))()
            # for some reason __qualname__ cannot be set in type()
            # so we have to set it here.
            try:
                task.__qualname__ = fun.__qualname__
            except AttributeError:
                pass
            self._tasks[task.name] = task
            task.bind(self)  # connects task to this app

            autoretry_for = tuple(
                options.get('autoretry_for',
                            getattr(task, 'autoretry_for', ()))
            )
            retry_kwargs = options.get(
                'retry_kwargs', getattr(task, 'retry_kwargs', {})
            )
            retry_backoff = int(
                options.get('retry_backoff',
                            getattr(task, 'retry_backoff', False))
            )
            retry_backoff_max = int(
                options.get('retry_backoff_max',
                            getattr(task, 'retry_backoff_max', 600))
            )
            retry_jitter = options.get(
                'retry_jitter', getattr(task, 'retry_jitter', True)
            )

            if autoretry_for and not hasattr(task, '_orig_run'):

                @wraps(task.run)
                def run(*args, **kwargs):
                    try:
                        return task._orig_run(*args, **kwargs)
                    except Ignore:
                        # If Ignore signal occures task shouldn't be retried,
                        # even if it suits autoretry_for list
                        raise
                    except Retry:
                        raise
                    except autoretry_for as exc:
                        if retry_backoff:
                            retry_kwargs['countdown'] = \
                                get_exponential_backoff_interval(
                                    factor=retry_backoff,
                                    retries=task.request.retries,
                                    maximum=retry_backoff_max,
                                    full_jitter=retry_jitter)
                        raise task.retry(exc=exc, **retry_kwargs)

                task._orig_run, task.run = task.run, run
        else:
            task = self._tasks[name]
        return task