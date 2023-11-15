    def __init__(self, n_jobs=1, backend=None, verbose=0, pre_dispatch='all',
                 temp_folder=None, max_nbytes=100e6, mmap_mode='r'):
        self.verbose = verbose
        self._mp_context = None
        if backend is None:
            backend = "multiprocessing"
        elif hasattr(backend, 'Pool') and hasattr(backend, 'Lock'):
            # Make it possible to pass a custom multiprocessing context as
            # backend to change the start method to forkserver or spawn or
            # preload modules on the forkserver helper process.
            self._mp_context = backend
            backend = "multiprocessing"
        if backend not in VALID_BACKENDS:
            raise ValueError("Invalid backend: %s, expected one of %r"
                             % (backend, VALID_BACKENDS))
        self.backend = backend
        self.n_jobs = n_jobs
        self.pre_dispatch = pre_dispatch
        self._pool = None
        self._temp_folder = temp_folder
        if isinstance(max_nbytes, _basestring):
            self._max_nbytes = 1024 * memstr_to_kbytes(max_nbytes)
        else:
            self._max_nbytes = max_nbytes
        self._mmap_mode = mmap_mode
        # Not starting the pool in the __init__ is a design decision, to be
        # able to close it ASAP, and not burden the user with closing it.
        self._output = None
        self._jobs = list()
        # A flag used to abort the dispatching of jobs in case an
        # exception is found
        self._aborting = False