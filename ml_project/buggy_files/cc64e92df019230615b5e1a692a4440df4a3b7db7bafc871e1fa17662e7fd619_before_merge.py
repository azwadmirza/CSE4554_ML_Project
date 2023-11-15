    def __init__(self, pool, *, connect_args, connect_kwargs,
                 max_queries, setup, init, max_inactive_time):

        self._pool = pool
        self._con = None

        self._connect_args = connect_args
        self._connect_kwargs = connect_kwargs
        self._max_queries = max_queries
        self._max_inactive_time = max_inactive_time
        self._setup = setup
        self._init = init
        self._inactive_callback = None
        self._in_use = False