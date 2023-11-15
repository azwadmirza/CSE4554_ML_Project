        def runTask():
            log.debug("Running task %s", task.task_id.value)
            sendUpdate(mesos_pb2.TASK_RUNNING)
            # This is where task.data is first invoked. Using this position to setup cleanupInfo
            taskData = pickle.loads(task.data)
            if self.workerCleanupInfo is not None:
                assert self.workerCleanupInfo == taskData.workerCleanupInfo
            else:
                self.workerCleanupInfo = taskData.workerCleanupInfo
            popen = runJob(taskData)
            self.runningTasks[task.task_id.value] = popen.pid
            try:
                exitStatus = popen.wait()
                if 0 == exitStatus:
                    sendUpdate(mesos_pb2.TASK_FINISHED)
                elif -9 == exitStatus:
                    sendUpdate(mesos_pb2.TASK_KILLED)
                else:
                    sendUpdate(mesos_pb2.TASK_FAILED, message=str(exitStatus))
            except:
                exc_type, exc_value, exc_trace = sys.exc_info()
                sendUpdate(mesos_pb2.TASK_FAILED,
                           message=str(traceback.format_exception_only(exc_type, exc_value)))
            finally:
                del self.runningTasks[task.task_id.value]