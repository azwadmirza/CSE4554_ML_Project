    def launch_task(self, task_id, executable, *args, **kwargs):
        """Handle the actual submission of the task to the executor layer.

        If the app task has the sites attributes not set (default=='all')
        the task is launched on a randomly selected executor from the
        list of executors. This behavior could later be updates to support
        binding to sites based on user specified criteria.

        If the app task specifies a particular set of sites, it will be
        targetted at those specific sites.

        Args:
            task_id (uuid string) : A uuid string that uniquely identifies the task
            executable (callable) : A callable object
            args (list of positional args)
            kwargs (arbitrary keyword arguments)


        Returns:
            Future that tracks the execution of the submitted executable
        """
        hit, memo_fu = self.memoizer.check_memo(task_id, self.tasks[task_id])
        if hit:
            self.handle_update(task_id, memo_fu, memo_cbk=True)
            return memo_fu

        target_sites = self.tasks[task_id]["sites"]
        executor = None
        if isinstance(target_sites, str) and target_sites.lower() == 'all':
            # Pick a random site from the list
            site, executor = random.choice(list(self.executors.items()))

        elif isinstance(target_sites, list):
            # Pick a random site from user specified list
            try:
                site = random.choice(target_sites)
                executor = self.executors[site]

            except Exception as e:
                logger.error("Task {}: requests invalid site [{}]".format(task_id,
                                                                          target_sites))
        else:
            logger.error("App {} specifies invalid site option, expects str|list".format(
                self.tasks[task_id]['func'].__name__))

        exec_fu = executor.submit(executable, *args, **kwargs)
        exec_fu.retries_left = self.fail_retries - \
            self.tasks[task_id]['fail_count']
        exec_fu.add_done_callback(partial(self.handle_update, task_id))
        logger.info("Task {} launched on site {}".format(task_id, site))
        return exec_fu