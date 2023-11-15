    def describe(self):
        result = {
            "jobDefinition": self.job_definition.arn,
            "jobId": self.job_id,
            "jobName": self.job_name,
            "jobQueue": self.job_queue.arn,
            "status": self.job_state,
            "dependsOn": [],
        }
        if result["status"] not in ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING"]:
            result["startedAt"] = datetime2int(self.job_started_at)
        if self.job_stopped:
            result["stoppedAt"] = datetime2int(self.job_stopped_at)
            result["container"] = {}
            result["container"]["command"] = [
                '/bin/sh -c "for a in `seq 1 10`; do echo Hello World; sleep 1; done"'
            ]
            result["container"]["privileged"] = False
            result["container"]["readonlyRootFilesystem"] = False
            result["container"]["ulimits"] = {}
            result["container"]["vcpus"] = 1
            result["container"]["volumes"] = ""
            result["container"]["logStreamName"] = self.log_stream_name
        if self.job_stopped_reason is not None:
            result["statusReason"] = self.job_stopped_reason
        return result