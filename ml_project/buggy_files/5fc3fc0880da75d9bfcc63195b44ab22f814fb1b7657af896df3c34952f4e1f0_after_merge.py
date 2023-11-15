    def __init__(self,
                 retry_period=300.0,
                 submit_size_limit=1000,
                 max_time_publishing=30.0,
                 backup_storage_limit_gb=None,
                 topic_replace_list=[],
                 gather_timing_data=False,
                 readonly=False,
                 process_loop_in_greenlet=False,
                 capture_device_data=True,
                 capture_log_data=True,
                 capture_analysis_data=True,
                 capture_record_data=True,
                 **kwargs):

        super(BaseHistorianAgent, self).__init__(**kwargs)
        # This should resemble a dictionary that has key's from and to which
        # will be replaced within the topics before it's stored in the
        # cache database
        self._process_loop_in_greenlet = process_loop_in_greenlet
        self._topic_replace_list = topic_replace_list

        _log.info('Topic string replace list: {}'
                  .format(self._topic_replace_list))

        self.gather_timing_data = bool(gather_timing_data)

        self.volttron_table_defs = 'volttron_table_definitions'
        self._backup_storage_limit_gb = backup_storage_limit_gb
        self._retry_period = float(retry_period)
        self._submit_size_limit = int(submit_size_limit)
        self._max_time_publishing = float(max_time_publishing)
        self._successful_published = set()
        # Remove the need to reset subscriptions to eliminate possible data
        # loss at config change.
        self._current_subscriptions = set()
        self._topic_replace_map = {}
        self._event_queue = gevent.queue.Queue() if self._process_loop_in_greenlet else Queue()
        self._readonly = bool(readonly)
        self._stop_process_loop = False
        self._process_thread = None

        self.no_insert = False
        self.no_query = False
        self.instance_name = None

        self._default_config = {"retry_period":self._retry_period,
                               "submit_size_limit": self._submit_size_limit,
                               "max_time_publishing": self._max_time_publishing,
                               "backup_storage_limit_gb": self._backup_storage_limit_gb,
                               "topic_replace_list": self._topic_replace_list,
                               "gather_timing_data": self.gather_timing_data,
                               "readonly": self._readonly,
                               "capture_device_data": capture_device_data,
                               "capture_log_data": capture_log_data,
                               "capture_analysis_data": capture_analysis_data,
                               "capture_record_data": capture_record_data
                               }

        self.vip.config.set_default("config", self._default_config)
        self.vip.config.subscribe(self._configure, actions=["NEW", "UPDATE"], pattern="config")