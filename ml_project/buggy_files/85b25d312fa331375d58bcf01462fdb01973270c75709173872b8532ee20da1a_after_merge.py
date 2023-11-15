    def wait_for_current_tasks(self):
        """Waits for all tasks in the task list to be completed, by waiting for their
        AppFuture to be completed. This method will not necessarily wait for any tasks
        added after cleanup has started (such as data stageout?)
        """

        logger.info("Waiting for all remaining tasks to complete")
        for task_id in list(self.tasks):
            # .exception() is a less exception throwing way of
            # waiting for completion than .result()
            if task_id not in self.tasks:
                logger.debug("Task {} no longer in task list".format(task_id))
            else:
                fut = self.tasks[task_id]['app_fu']
                if not fut.done():
                    logger.debug("Waiting for task {} to complete".format(task_id))
                    fut.exception()
        logger.info("All remaining tasks completed")