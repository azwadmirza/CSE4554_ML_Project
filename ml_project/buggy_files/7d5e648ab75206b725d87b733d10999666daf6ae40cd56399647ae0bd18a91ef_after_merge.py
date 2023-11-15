    def prepare_steps(self, args, kwargs, tasks,
                      root_id=None, parent_id=None, link_error=None, app=None,
                      last_task_id=None, group_id=None, chord_body=None,
                      clone=True, from_dict=Signature.from_dict):
        app = app or self.app
        # use chain message field for protocol 2 and later.
        # this avoids pickle blowing the stack on the recursion
        # required by linking task together in a tree structure.
        # (why is pickle using recursion? or better yet why cannot python
        #  do tail call optimization making recursion actually useful?)
        use_link = self._use_link
        if use_link is None and app.conf.task_protocol == 1:
            use_link = True
        steps = deque(tasks)

        steps_pop = steps.pop
        steps_extend = steps.extend

        prev_task = None
        prev_res = None
        tasks, results = [], []
        i = 0
        # NOTE: We are doing this in reverse order.
        # The result is a list of tasks in reverse order, that is
        # passed as the ``chain`` message field.
        # As it's reversed the worker can just do ``chain.pop()`` to
        # get the next task in the chain.
        while steps:
            task = steps_pop()
            is_first_task, is_last_task = not steps, not i

            if not isinstance(task, abstract.CallableSignature):
                task = from_dict(task, app=app)
            if isinstance(task, group):
                task = maybe_unroll_group(task)

            # first task gets partial args from chain
            if clone:
                if is_first_task:
                    task = task.clone(args, kwargs)
                else:
                    task = task.clone()
            elif is_first_task:
                task.args = tuple(args) + tuple(task.args)

            if isinstance(task, _chain):
                # splice the chain
                steps_extend(task.tasks)
                continue

            if isinstance(task, group) and prev_task:
                # automatically upgrade group(...) | s to chord(group, s)
                # for chords we freeze by pretending it's a normal
                # signature instead of a group.
                tasks.pop()
                results.pop()
                try:
                    task = chord(
                        task, body=prev_task,
                        task_id=prev_res.task_id, root_id=root_id, app=app,
                    )
                except AttributeError:
                    # A GroupResult does not have a task_id since it consists
                    # of multiple tasks.
                    # We therefore, have to construct the chord without it.
                    # Issues #5467, #3585.
                    task = chord(
                        task, body=prev_task,
                        root_id=root_id, app=app,
                    )

            if is_last_task:
                # chain(task_id=id) means task id is set for the last task
                # in the chain.  If the chord is part of a chord/group
                # then that chord/group must synchronize based on the
                # last task in the chain, so we only set the group_id and
                # chord callback for the last task.
                res = task.freeze(
                    last_task_id,
                    root_id=root_id, group_id=group_id, chord=chord_body,
                )
            else:
                res = task.freeze(root_id=root_id)

            i += 1

            if prev_task:
                if use_link:
                    # link previous task to this task.
                    task.link(prev_task)

                if prev_res and not prev_res.parent:
                    prev_res.parent = res

            if link_error:
                for errback in maybe_list(link_error):
                    task.link_error(errback)

            tasks.append(task)
            results.append(res)

            prev_task, prev_res = task, res
            if isinstance(task, chord):
                app.backend.ensure_chords_allowed()
                # If the task is a chord, and the body is a chain
                # the chain has already been prepared, and res is
                # set to the last task in the callback chain.

                # We need to change that so that it points to the
                # group result object.
                node = res
                while node.parent:
                    node = node.parent
                prev_res = node
        return tasks, results