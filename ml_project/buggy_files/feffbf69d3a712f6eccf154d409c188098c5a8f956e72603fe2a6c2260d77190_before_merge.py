    def checkpoint(self):
        """Checkpoint the dfk incrementally to a checkpoint file.

        When called, every task that has been completed yet not
        checkpointed is checkpointed to a file.

        .. note::
            Checkpointing only works if memoization is enabled

        Returns:
            Checkpoint dir if checkpoints were written successfully.
            By default the checkpoints are written to the RUNDIR of the current
            run under RUNDIR/checkpoints/{tasks.pkl, dfk.pkl}
        """
        logger.info("Checkpointing.. ")

        checkpoint_dir = '{0}/checkpoint'.format(self.rundir)
        checkpoint_dfk = checkpoint_dir + '/dfk.pkl'
        checkpoint_tasks = checkpoint_dir + '/tasks.pkl'

        if not os.path.exists(checkpoint_dir):
            try:
                os.makedirs(checkpoint_dir)
            except FileExistsError as e:
                pass

        with open(checkpoint_dfk, 'wb') as f:
            state = {'config': self.config,
                     'rundir': self.rundir,
                     'task_count': self.task_count
                     }
            pickle.dump(state, f)

        count = 0
        with open(checkpoint_tasks, 'ab') as f:
            for task_id in self.tasks:
                if self.tasks[task_id]['app_fu'].done() and \
                   not self.tasks[task_id]['checkpoint']:
                    hashsum = self.tasks[task_id]['hashsum']
                    if not hashsum:
                        continue
                    t = {'hash': hashsum,
                         'exception': None,
                         'result': None}
                    try:
                        # Asking for the result will raise an exception if
                        # the app had failed. Should we even checkpoint these?
                        # TODO : Resolve this question ?
                        r = self.memoizer.hash_lookup(hashsum).result()
                    except Exception as e:
                        t['exception'] = e
                    else:
                        t['result'] = r

                    # We are using pickle here since pickle dumps to a file in 'ab'
                    # mode behave like a incremental log.
                    pickle.dump(t, f)
                    count += 1
                    self.tasks[task_id]['checkpoint'] = True
                    logger.debug("Task {} checkpointed".format(task_id))

        self.checkpointed_tasks += count

        if count == 0:
            if self.checkpointed_tasks == 0:
                logger.warn("No tasks checkpointed, please ensure caching is enabled")
            else:
                logger.debug("No tasks checkpointed")
        else:
            logger.info("Done checkpointing {} tasks".format(count))

        return checkpoint_dir