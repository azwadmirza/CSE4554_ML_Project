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