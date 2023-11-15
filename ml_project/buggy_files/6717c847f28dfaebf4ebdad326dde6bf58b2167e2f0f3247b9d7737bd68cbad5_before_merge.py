    def _setup_runner(self):
        self.status = Trial.RUNNING
        trainable_cls = get_registry().get(
            TRAINABLE_CLASS, self.trainable_name)
        cls = ray.remote(
            num_cpus=self.resources.driver_cpu_limit,
            num_gpus=self.resources.driver_gpu_limit)(trainable_cls)
        if not self.result_logger:
            if not os.path.exists(self.local_dir):
                os.makedirs(self.local_dir)
            self.logdir = tempfile.mkdtemp(
                prefix="{}_{}".format(
                    str(self)[:MAX_LEN_IDENTIFIER], date_str()),
                dir=self.local_dir)
            self.result_logger = UnifiedLogger(
                self.config, self.logdir, self.upload_dir)
        remote_logdir = self.logdir

        def logger_creator(config):
            # Set the working dir in the remote process, for user file writes
            if not os.path.exists(remote_logdir):
                os.makedirs(remote_logdir)
            os.chdir(remote_logdir)
            return NoopLogger(config, remote_logdir)

        # Logging for trials is handled centrally by TrialRunner, so
        # configure the remote runner to use a noop-logger.
        self.runner = cls.remote(
            config=self.config, registry=get_registry(),
            logger_creator=logger_creator)