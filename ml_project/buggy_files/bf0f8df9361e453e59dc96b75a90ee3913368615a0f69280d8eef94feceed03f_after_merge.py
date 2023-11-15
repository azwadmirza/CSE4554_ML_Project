    def __init__(
            self, url_or_fetch_strategy,
            name=None, mirror_path=None, keep=False, path=None, lock=True):
        """Create a stage object.
           Parameters:
             url_or_fetch_strategy
                 URL of the archive to be downloaded into this stage, OR
                 a valid FetchStrategy.

             name
                 If a name is provided, then this stage is a named stage
                 and will persist between runs (or if you construct another
                 stage object later).  If name is not provided, then this
                 stage will be given a unique name automatically.

             mirror_path
                 If provided, Stage will search Spack's mirrors for
                 this archive at the mirror_path, before using the
                 default fetch strategy.

             keep
                 By default, when used as a context manager, the Stage
                 is deleted on exit when no exceptions are raised.
                 Pass True to keep the stage intact even if no
                 exceptions are raised.
        """
        # TODO: fetch/stage coupling needs to be reworked -- the logic
        # TODO: here is convoluted and not modular enough.
        if isinstance(url_or_fetch_strategy, basestring):
            self.fetcher = fs.from_url(url_or_fetch_strategy)
        elif isinstance(url_or_fetch_strategy, fs.FetchStrategy):
            self.fetcher = url_or_fetch_strategy
        else:
            raise ValueError(
                "Can't construct Stage without url or fetch strategy")
        self.fetcher.set_stage(self)
        # self.fetcher can change with mirrors.
        self.default_fetcher = self.fetcher
        # used for mirrored archives of repositories.
        self.skip_checksum_for_mirror = True

        # TODO : this uses a protected member of tempfile, but seemed the only
        # TODO : way to get a temporary name besides, the temporary link name
        # TODO : won't be the same as the temporary stage area in tmp_root
        self.name = name
        if name is None:
            self.name = STAGE_PREFIX + next(tempfile._get_candidate_names())
        self.mirror_path = mirror_path
        self.tmp_root = find_tmp_root()

        # Try to construct here a temporary name for the stage directory
        # If this is a named stage, then construct a named path.
        if path is not None:
            self.path = path
        else:
            self.path = join_path(spack.stage_path, self.name)

        # Flag to decide whether to delete the stage folder on exit or not
        self.keep = keep

        # File lock for the stage directory.  We use one file for all
        # stage locks. See Spec.prefix_lock for details on this approach.
        self._lock = None
        if lock:
            if self.name not in Stage.stage_locks:
                sha1 = hashlib.sha1(self.name).digest()
                lock_id = prefix_bits(sha1, bit_length(sys.maxsize))
                stage_lock_path = join_path(spack.stage_path, '.lock')

                Stage.stage_locks[self.name] = llnl.util.lock.Lock(
                    stage_lock_path, lock_id, 1)

            self._lock = Stage.stage_locks[self.name]