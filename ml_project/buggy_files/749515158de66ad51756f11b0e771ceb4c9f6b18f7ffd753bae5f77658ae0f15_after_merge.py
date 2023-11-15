    def setup_once():
        import celery.app.trace as trace  # type: ignore

        old_build_tracer = trace.build_tracer

        def sentry_build_tracer(name, task, *args, **kwargs):
            # Need to patch both methods because older celery sometimes
            # short-circuits to task.run if it thinks it's safe.
            task.__call__ = _wrap_task_call(task, task.__call__)
            task.run = _wrap_task_call(task, task.run)
            return _wrap_tracer(task, old_build_tracer(name, task, *args, **kwargs))

        trace.build_tracer = sentry_build_tracer

        _patch_worker_exit()

        # This logger logs every status of every task that ran on the worker.
        # Meaning that every task's breadcrumbs are full of stuff like "Task
        # <foo> raised unexpected <bar>".
        ignore_logger("celery.worker.job")