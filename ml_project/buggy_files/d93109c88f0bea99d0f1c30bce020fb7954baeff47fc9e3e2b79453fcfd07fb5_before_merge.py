        def runTask():
            log.debug("Running task %s", task.task_id.value)
            sendUpdate(mesos_pb2.TASK_RUNNING)
            popen = runJob(pickle.loads(task.data))
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
                sendUpdate(mesos_pb2.TASK_FAILED, message=str(traceback.format_exception_only(exc_type, exc_value)))
            finally:
                del self.runningTasks[task.task_id.value]