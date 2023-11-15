    def __init__(
        self,
        scheduler: Scheduler,
        period_secs=10,
        lease_extension_interval_secs=(30 * 60),
        gc_interval_secs=(4 * 60 * 60),
    ):
        super().__init__()
        self._scheduler_session = scheduler.new_session(build_id="store_gc_service_session")
        self._logger = logging.getLogger(__name__)

        self._period_secs = period_secs
        self._lease_extension_interval_secs = lease_extension_interval_secs
        self._gc_interval_secs = gc_interval_secs

        self._set_next_gc()
        self._set_next_lease_extension()