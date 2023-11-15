    def run(self):
        """
        Run the container.

        Logic is as follows:
        Generate container info (eventually from task definition)
        Start container
        Loop whilst not asked to stop and the container is running.
          Get all logs from container between the last time I checked and now.
        Convert logs into cloudwatch format
        Put logs into cloudwatch

        :return:
        """
        try:
            self.job_state = "PENDING"

            image = self.job_definition.container_properties.get(
                "image", "alpine:latest"
            )
            privileged = self.job_definition.container_properties.get(
                "privileged", False
            )
            cmd = self._get_container_property(
                "command",
                '/bin/sh -c "for a in `seq 1 10`; do echo Hello World; sleep 1; done"',
            )
            environment = {
                e["name"]: e["value"]
                for e in self._get_container_property("environment", [])
            }
            volumes = {
                v["name"]: v["host"]
                for v in self._get_container_property("volumes", [])
            }
            mounts = [
                docker.types.Mount(
                    m["containerPath"],
                    volumes[m["sourceVolume"]]["sourcePath"],
                    type="bind",
                    read_only=m["readOnly"],
                )
                for m in self._get_container_property("mountPoints", [])
            ]
            name = "{0}-{1}".format(self.job_name, self.job_id)

            self.job_state = "RUNNABLE"
            # TODO setup ecs container instance

            self.job_started_at = datetime.datetime.now()
            self.job_state = "STARTING"
            log_config = docker.types.LogConfig(type=docker.types.LogConfig.types.JSON)
            container = self.docker_client.containers.run(
                image,
                cmd,
                detach=True,
                name=name,
                log_config=log_config,
                environment=environment,
                mounts=mounts,
                privileged=privileged,
            )
            self.job_state = "RUNNING"
            try:
                container.reload()
                while container.status == "running" and not self.stop:
                    container.reload()

                # Container should be stopped by this point... unless asked to stop
                if container.status == "running":
                    container.kill()

                # Log collection
                logs_stdout = []
                logs_stderr = []
                logs_stderr.extend(
                    container.logs(
                        stdout=False,
                        stderr=True,
                        timestamps=True,
                        since=datetime2int(self.job_started_at),
                    )
                    .decode()
                    .split("\n")
                )
                logs_stdout.extend(
                    container.logs(
                        stdout=True,
                        stderr=False,
                        timestamps=True,
                        since=datetime2int(self.job_started_at),
                    )
                    .decode()
                    .split("\n")
                )

                # Process logs
                logs_stdout = [x for x in logs_stdout if len(x) > 0]
                logs_stderr = [x for x in logs_stderr if len(x) > 0]
                logs = []
                for line in logs_stdout + logs_stderr:
                    date, line = line.split(" ", 1)
                    date = dateutil.parser.parse(date)
                    # TODO: Replace with int(date.timestamp()) once we yeet Python2 out of the window
                    date = int(
                        (time.mktime(date.timetuple()) + date.microsecond / 1000000.0)
                    )
                    logs.append({"timestamp": date, "message": line.strip()})

                # Send to cloudwatch
                log_group = "/aws/batch/job"
                stream_name = "{0}/default/{1}".format(
                    self.job_definition.name, self.job_id
                )
                self.log_stream_name = stream_name
                self._log_backend.ensure_log_group(log_group, None)
                self._log_backend.create_log_stream(log_group, stream_name)
                self._log_backend.put_log_events(log_group, stream_name, logs, None)

                self.job_state = "SUCCEEDED" if not self.stop else "FAILED"

            except Exception as err:
                logger.error(
                    "Failed to run AWS Batch container {0}. Error {1}".format(
                        self.name, err
                    )
                )
                self.job_state = "FAILED"
                container.kill()
            finally:
                container.remove()
        except Exception as err:
            logger.error(
                "Failed to run AWS Batch container {0}. Error {1}".format(
                    self.name, err
                )
            )
            self.job_state = "FAILED"

        self.job_stopped = True
        self.job_stopped_at = datetime.datetime.now()