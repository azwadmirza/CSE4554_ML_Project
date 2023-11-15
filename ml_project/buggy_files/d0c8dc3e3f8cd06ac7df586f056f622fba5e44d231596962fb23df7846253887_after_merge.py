    def __init__(self, processes=None, temp_folder=None, max_nbytes=1e6,
                 mmap_mode='r', forward_reducers=None, backward_reducers=None,
                 verbose=0, context_id=None, prewarm=False, **kwargs):
        if forward_reducers is None:
            forward_reducers = dict()
        if backward_reducers is None:
            backward_reducers = dict()

        # Prepare a sub-folder name for the serialization of this particular
        # pool instance (do not create in advance to spare FS write access if
        # no array is to be dumped):
        use_shared_mem = False
        pool_folder_name = "joblib_memmaping_pool_%d_%d" % (
            os.getpid(), id(self))
        if temp_folder is None:
            temp_folder = os.environ.get('JOBLIB_TEMP_FOLDER', None)
        if temp_folder is None:
            if os.path.exists(SYSTEM_SHARED_MEM_FS):
                try:
                    temp_folder = SYSTEM_SHARED_MEM_FS
                    pool_folder = os.path.join(temp_folder, pool_folder_name)
                    if not os.path.exists(pool_folder):
                        os.makedirs(pool_folder)
                    use_shared_mem = True
                except IOError:
                    # Missing rights in the the /dev/shm partition,
                    # fallback to regular temp folder.
                    temp_folder = None
        if temp_folder is None:
            # Fallback to the default tmp folder, typically /tmp
            temp_folder = tempfile.gettempdir()
        temp_folder = os.path.abspath(os.path.expanduser(temp_folder))
        pool_folder = os.path.join(temp_folder, pool_folder_name)
        self._temp_folder = pool_folder

        # Register the garbage collector at program exit in case caller forgets
        # to call terminate explicitly: note we do not pass any reference to
        # self to ensure that this callback won't prevent garbage collection of
        # the pool instance and related file handler resources such as POSIX
        # semaphores and pipes
        atexit.register(lambda: delete_folder(pool_folder))

        if np is not None:
            # Register smart numpy.ndarray reducers that detects memmap backed
            # arrays and that is alse able to dump to memmap large in-memory
            # arrays over the max_nbytes threshold
            if prewarm == "auto":
                prewarm = not use_shared_mem
            forward_reduce_ndarray = ArrayMemmapReducer(
                max_nbytes, pool_folder, mmap_mode, verbose,
                context_id=context_id, prewarm=prewarm)
            forward_reducers[np.ndarray] = forward_reduce_ndarray
            forward_reducers[np.memmap] = reduce_memmap

            # Communication from child process to the parent process always
            # pickles in-memory numpy.ndarray without dumping them as memmap
            # to avoid confusing the caller and make it tricky to collect the
            # temporary folder
            backward_reduce_ndarray = ArrayMemmapReducer(
                None, pool_folder, mmap_mode, verbose)
            backward_reducers[np.ndarray] = backward_reduce_ndarray
            backward_reducers[np.memmap] = reduce_memmap

        poolargs = dict(
            processes=processes,
            forward_reducers=forward_reducers,
            backward_reducers=backward_reducers)
        poolargs.update(kwargs)
        super(MemmapingPool, self).__init__(**poolargs)