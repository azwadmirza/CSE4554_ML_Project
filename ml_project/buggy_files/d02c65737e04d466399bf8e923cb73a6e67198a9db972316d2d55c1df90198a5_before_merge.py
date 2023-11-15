        def sentry_build_tracer(name, task, *args, **kwargs):
            # Need to patch both methods because older celery sometimes
            # short-circuits to task.run if it thinks it's safe.
            task.__call__ = _wrap_task_call(task.__call__)
            task.run = _wrap_task_call(task.run)
            return _wrap_tracer(task, old_build_tracer(name, task, *args, **kwargs))