    def __init__(self, name, job_def, job_queue, log_backend, container_overrides):
        """
        Docker Job

        :param name: Job Name
        :param job_def: Job definition
        :type: job_def: JobDefinition
        :param job_queue: Job Queue
        :param log_backend: Log backend
        :type log_backend: moto.logs.models.LogsBackend
        """
        threading.Thread.__init__(self)

        self.job_name = name
        self.job_id = str(uuid.uuid4())
        self.job_definition = job_def
        self.container_overrides = container_overrides or {}
        self.job_queue = job_queue
        self.job_state = "SUBMITTED"  # One of SUBMITTED | PENDING | RUNNABLE | STARTING | RUNNING | SUCCEEDED | FAILED
        self.job_queue.jobs.append(self)
        self.job_started_at = datetime.datetime(1970, 1, 1)
        self.job_stopped_at = datetime.datetime(1970, 1, 1)
        self.job_stopped = False
        self.job_stopped_reason = None

        self.stop = False

        self.daemon = True
        self.name = "MOTO-BATCH-" + self.job_id

        self.docker_client = docker.from_env()
        self._log_backend = log_backend
        self.log_stream_name = None

        # Unfortunately mocking replaces this method w/o fallback enabled, so we
        # need to replace it if we detect it's been mocked
        if requests.adapters.HTTPAdapter.send != _orig_adapter_send:
            _orig_get_adapter = self.docker_client.api.get_adapter

            def replace_adapter_send(*args, **kwargs):
                adapter = _orig_get_adapter(*args, **kwargs)

                if isinstance(adapter, requests.adapters.HTTPAdapter):
                    adapter.send = functools.partial(_orig_adapter_send, adapter)
                return adapter

            self.docker_client.api.get_adapter = replace_adapter_send