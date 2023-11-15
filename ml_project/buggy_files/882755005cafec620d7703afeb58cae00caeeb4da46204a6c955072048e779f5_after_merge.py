    def __init__(self, **kwargs):
        self._cluster_info_ref = None
        self._session_manager_ref = None
        self._assigner_ref = None
        self._resource_ref = None
        self._chunk_meta_ref = None
        self._kv_store_ref = None
        self._node_info_ref = None
        self._result_receiver_ref = None

        options.scheduler.enable_failover = not (kwargs.pop('disable_failover', None) or False)

        if kwargs:  # pragma: no cover
            raise TypeError('Keyword arguments %r cannot be recognized.' % ', '.join(kwargs))