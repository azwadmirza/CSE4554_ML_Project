    def __init__(self):
        """Start opsdroid."""
        self.bot_name = 'opsdroid'
        self.sys_status = 0
        self.connectors = []
        self.connector_tasks = []
        self.eventloop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            self.eventloop.add_signal_handler(sig, self.stop)
        self.skills = []
        self.memory = Memory()
        self.loader = Loader(self)
        self.config = {}
        self.stats = {
            "messages_parsed": 0,
            "webhooks_called": 0,
            "total_response_time": 0,
            "total_responses": 0,
        }
        self.web_server = None
        self.should_restart = False
        self.stored_path = []
        _LOGGER.info("Created main opsdroid object")