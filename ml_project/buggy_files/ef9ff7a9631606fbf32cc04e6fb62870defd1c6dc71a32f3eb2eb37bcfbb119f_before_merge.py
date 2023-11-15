    def __init__(
        self,
        name: str = None,
        labels: Iterable[str] = None,
        env_vars: dict = None,
        max_polls: int = None,
        agent_address: str = None,
        no_cloud_logs: bool = False,
    ) -> None:
        self.name = name or config.cloud.agent.get("name", "agent")
        self.labels = list(
            labels or ast.literal_eval(config.cloud.agent.get("labels", "[]"))
        )
        self.env_vars = env_vars or config.cloud.agent.get("env_vars", dict())
        self.max_polls = max_polls
        self.log_to_cloud = False if no_cloud_logs else True

        self.agent_address = agent_address or config.cloud.agent.get(
            "agent_address", ""
        )
        self._api_server = None  # type: ignore
        self._api_server_loop = None  # type: Optional[IOLoop]
        self._api_server_thread = None  # type: Optional[threading.Thread]

        logger = logging.getLogger(self.name)
        logger.setLevel(config.cloud.agent.get("level"))
        if not any([isinstance(h, logging.StreamHandler) for h in logger.handlers]):
            ch = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(context.config.logging.format)
            formatter.converter = time.gmtime  # type: ignore
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        self.logger = logger
        self.submitting_flow_runs = set()  # type: Set[str]

        self.logger.debug("Verbose logs enabled")
        self.logger.debug(f"Environment variables: {[*self.env_vars]}")
        self.logger.debug(f"Max polls: {self.max_polls}")
        self.logger.debug(f"Agent address: {self.agent_address}")
        self.logger.debug(f"Log to Cloud: {self.log_to_cloud}")

        token = config.cloud.agent.get("auth_token")

        self.logger.debug(f"Prefect backend: {config.backend}")

        self.client = Client(api_token=token)
        if config.backend == "cloud":
            self._verify_token(token)
            self.client.attach_headers({"X-PREFECT-AGENT-ID": self._register_agent()})