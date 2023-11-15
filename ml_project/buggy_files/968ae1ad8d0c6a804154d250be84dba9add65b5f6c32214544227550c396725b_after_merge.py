    def _call_task_errbacks(self, request, exc, traceback):
        old_signature = []
        for errback in request.errbacks:
            errback = self.app.signature(errback)
            if (
                # workaround to support tasks with bind=True executed as
                # link errors. Otherwise retries can't be used
                not isinstance(errback.type.__header__, partial) and
                arity_greater(errback.type.__header__, 1)
            ):
                errback(request, exc, traceback)
            else:
                old_signature.append(errback)
        if old_signature:
            # Previously errback was called as a task so we still
            # need to do so if the errback only takes a single task_id arg.
            task_id = request.id
            root_id = request.root_id or task_id
            group(old_signature, app=self.app).apply_async(
                (task_id,), parent_id=task_id, root_id=root_id
            )