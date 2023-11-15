    def __init__(self, destination_vip, destination_serverkey,
                 custom_topic_list=[],
                 topic_replace_list=[],
                 required_target_agents=[],
                 cache_only=False, **kwargs):
        kwargs["process_loop_in_greenlet"] = True
        super(ForwardHistorian, self).__init__(**kwargs)

        # will be available in both threads.
        self._topic_replace_map = {}
        self.topic_replace_list = topic_replace_list
        self._num_failures = 0
        self._last_timeout = 0
        self._target_platform = None
        self._current_custom_topics = set()
        self.destination_vip = destination_vip
        self.destination_serverkey = destination_serverkey
        self.required_target_agents = required_target_agents
        self.cache_only = cache_only

        config = {"custom_topic_list": custom_topic_list,
                  "topic_replace_list": self.topic_replace_list,
                  "required_target_agents": self.required_target_agents,
                  "destination_vip": self.destination_vip,
                  "destination_serverkey": self.destination_serverkey,
                  "cache_only": self.cache_only}

        self.update_default_config(config)

        # We do not support the insert RPC call.
        self.no_insert = True
        # We do not support the query RPC call.
        self.no_query = True