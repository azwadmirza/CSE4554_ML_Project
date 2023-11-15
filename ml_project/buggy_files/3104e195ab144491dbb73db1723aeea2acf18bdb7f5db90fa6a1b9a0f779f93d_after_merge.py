    def handle_update(self, task_id, future, memo_cbk=False):
        """This function is called only as a callback from a task being done.

        Move done task from runnable -> done
        Move newly doable tasks from pending -> runnable , and launch

        Args:
             task_id (string) : Task id which is a uuid string
             future (Future) : The future object corresponding to the task which
             makes this callback

        KWargs:
             memo_cbk(Bool) : Indicates that the call is coming from a memo update,
             that does not require additional memo updates.
        """
        final_state_flag = False

        try:
            res = future.result()
            if isinstance(res, RemoteException):
                res.reraise()

        except Exception as e:
            logger.exception("Task {} failed".format(task_id))

            # We keep the history separately, since the future itself could be
            # tossed.
            self.tasks[task_id]['fail_history'].append(future._exception)
            self.tasks[task_id]['fail_count'] += 1

            if not self.lazy_fail:
                logger.debug("Eager fail, skipping retry logic")
                raise e

            if self.tasks[task_id]['fail_count'] <= self.fail_retries:
                logger.debug("Task {} marked for retry".format(task_id))
                self.tasks[task_id]['status'] = States.pending

            else:
                logger.info("Task {} failed after {} retry attempts".format(task_id,
                                                                            self.fail_retries))
                self.tasks[task_id]['status'] = States.failed
                final_state_flag = True

        else:
            logger.info("Task {} completed".format(task_id))
            self.tasks[task_id]['status'] = States.done
            final_state_flag = True

        if not memo_cbk and final_state_flag is True:
            # Update the memoizer with the new result if this is not a
            # result from a memo lookup and the task has reached a terminal state.
            self.memoizer.update_memo(task_id, self.tasks[task_id], future)

            if self.checkpoint_mode is 'task_exit':
                self.checkpoint(tasks=[task_id])

        # Identify tasks that have resolved dependencies and launch
        for tid in list(self.tasks):
            # Skip all non-pending tasks
            if self.tasks[tid]['status'] != States.pending:
                continue

            if self._count_deps(self.tasks[tid]['depends'], tid) == 0:
                # We can now launch *task*
                new_args, kwargs, exceptions = self.sanitize_and_wrap(task_id,
                                                                      self.tasks[tid]['args'],
                                                                      self.tasks[tid]['kwargs'])
                self.tasks[tid]['args'] = new_args
                self.tasks[tid]['kwargs'] = kwargs
                if not exceptions:
                    # There are no dependency errors
                    exec_fu = None
                    # Acquire a lock, retest the state, launch
                    with self.task_launch_lock:
                        if self.tasks[tid]['status'] == States.pending:
                            self.tasks[tid]['status'] = States.running
                            exec_fu = self.launch_task(
                                tid, self.tasks[tid]['func'], *new_args, **kwargs)

                    if exec_fu:
                        self.tasks[task_id]['exec_fu'] = exec_fu
                        try:
                            self.tasks[tid]['app_fu'].update_parent(exec_fu)
                            self.tasks[tid]['exec_fu'] = exec_fu
                        except AttributeError as e:
                            logger.error(
                                "Task {}: Caught AttributeError at update_parent".format(tid))
                            raise e
                else:
                    logger.info(
                        "Task {} deferred due to dependency failure".format(tid))
                    # Raise a dependency exception
                    self.tasks[tid]['status'] = States.dep_fail
                    try:
                        fu = Future()
                        fu.retries_left = 0
                        self.tasks[tid]['exec_fu'] = fu
                        self.tasks[tid]['app_fu'].update_parent(fu)
                        fu.set_exception(DependencyError(exceptions,
                                                         tid,
                                                         None))

                    except AttributeError as e:
                        logger.error(
                            "Task {} AttributeError at update_parent".format(tid))
                        raise e

        return