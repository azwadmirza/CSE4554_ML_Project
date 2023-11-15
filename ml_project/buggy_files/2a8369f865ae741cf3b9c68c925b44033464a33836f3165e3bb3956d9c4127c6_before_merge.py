    def launchTask(self, driver, task):
        """
        Invoked by SchedulerDriver when a Mesos task should be launched by this executor
        """

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

        def runJob(job):
            """
            :type job: toil.batchSystems.mesos.ToilJob

            :rtype: subprocess.Popen
            """
            if job.userScript:
                job.userScript.register()
            log.debug("Invoking command: '%s'", job.command)
            with self.popenLock:
                return subprocess.Popen(job.command,
                                        shell=True, env=dict(os.environ, **job.environment))

        def sendUpdate(taskState, message=''):
            log.debug("Sending status update ...")
            status = mesos_pb2.TaskStatus()
            status.task_id.value = task.task_id.value
            status.message = message
            status.state = taskState
            driver.sendStatusUpdate(status)
            log.debug("Sent status update")

        thread = threading.Thread(target=runTask)
        thread.start()