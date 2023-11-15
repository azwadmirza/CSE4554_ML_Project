    def from_dict(cls, d, app=None):
        # We need to mutate the `kwargs` element in place to avoid confusing
        # `freeze()` implementations which end up here and expect to be able to
        # access elements from that dictionary later and refer to objects
        # canonicalized here
        orig_tasks = d["kwargs"]["tasks"]
        d["kwargs"]["tasks"] = rebuilt_tasks = type(orig_tasks)((
            maybe_signature(task, app=app) for task in orig_tasks
        ))
        return _upgrade(
            d, group(rebuilt_tasks, app=app, **d['options']),
        )