    def __init__(self, discoverer, distributed=True):
        if isinstance(discoverer, list):
            discoverer = StaticSchedulerDiscoverer(discoverer)

        self._discoverer = discoverer
        self._distributed = distributed
        self._hash_ring = None
        self._watcher = None
        self._schedulers = []
        self._observer_refs = []