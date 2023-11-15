    def __init__(self, collection_interval=DEFAULT_COLLECTION_INTERVAL,
                 sleep_delay=DEFAULT_SLEEP_DELAY):
        """
        :param collection_interval: How often to check database for old data and perform garbage
               collection.
        :type collection_interval: ``int``

        :param sleep_delay: How long to sleep (in seconds) between collection of different object
                            types.
        :type sleep_delay: ``int``
        """
        self._collection_interval = collection_interval

        self._action_executions_ttl = cfg.CONF.garbagecollector.action_executions_ttl
        self._action_executions_output_ttl = cfg.CONF.garbagecollector.action_executions_output_ttl
        self._trigger_instances_ttl = cfg.CONF.garbagecollector.trigger_instances_ttl
        self._purge_inquiries = cfg.CONF.garbagecollector.purge_inquiries
        self._workflow_execution_max_idle = cfg.CONF.workflow_engine.gc_max_idle_sec

        self._validate_ttl_values()

        self._sleep_delay = sleep_delay