    def __init__(
        self,
        scheduler: Scheduler,
        period_secs=10,
        lease_extension_interval_secs=(15 * 60),
        gc_interval_secs=(1 * 60 * 60),
        target_size_bytes=(4 * 1024 * 1024 * 1024),
    ):
        super().__init__()
        self._scheduler_session = scheduler.new_session(
            zipkin_trace_v2=False, build_id="store_gc_service_session"
        )
        self._logger = logging.getLogger(__name__)

        self._period_secs = period_secs
        self._lease_extension_interval_secs = lease_extension_interval_secs
        self._gc_interval_secs = gc_interval_secs
        self._target_size_bytes = target_size_bytes

        self._set_next_gc()
        self._set_next_lease_extension()