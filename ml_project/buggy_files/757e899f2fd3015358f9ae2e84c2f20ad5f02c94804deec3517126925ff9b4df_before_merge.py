    def statusUpdate(self, driver, update):
        """
        Invoked when the status of a task has changed (e.g., a slave is lost and so the task is
        lost, a task finishes and an executor sends a status update saying so, etc). Note that
        returning from this callback _acknowledges_ receipt of this status update! If for
        whatever reason the scheduler aborts during this callback (or the process exits) another
        status update will be delivered (note, however, that this is currently not true if the
        slave sending the status update is lost/fails during that time).
        """
        taskID = int(update.task_id.value)
        stateName = mesos_pb2.TaskState.Name(update.state)
        log.debug('Task %i is in state %s', taskID, stateName)

        try:
            self.killSet.remove(taskID)
        except KeyError:
            pass
        else:
            self.killedSet.add(taskID)

        if update.state == mesos_pb2.TASK_FINISHED:
            self.__updateState(taskID, 0)
        elif update.state == mesos_pb2.TASK_FAILED:
            exitStatus = int(update.message)
            log.warning('Task %i failed with exit status %i', taskID, exitStatus)
            self.__updateState(taskID, exitStatus)
        elif update.state in (mesos_pb2.TASK_LOST, mesos_pb2.TASK_KILLED, mesos_pb2.TASK_ERROR):
            log.warning("Task %i is in unexpected state %s with message '%s'",
                        taskID, stateName, update.message)
            self.__updateState(taskID, 255)

        # Explicitly acknowledge the update if implicit acknowledgements are not being used.
        if not self.implicitAcknowledgements:
            driver.acknowledgeStatusUpdate(update)