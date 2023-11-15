    def __init__(
        self,
        filename,
        pp=None,
        script=None,
        nzb=None,
        futuretype=False,
        cat=None,
        url=None,
        priority=DEFAULT_PRIORITY,
        nzbname=None,
        status=Status.QUEUED,
        nzo_info=None,
        reuse=None,
        dup_check=True,
    ):
        TryList.__init__(self)

        self.filename = filename  # Original filename
        if nzbname and nzb:
            self.work_name = nzbname  # Use nzbname if set and only for non-future slot
        else:
            self.work_name = filename

        # For future-slots we keep the name given by URLGrabber
        if nzb is None:
            self.final_name = self.work_name = filename
        else:
            # Remove trailing .nzb and .par(2)
            self.work_name = create_work_name(self.work_name)

        # Extract password
        self.work_name, self.password = scan_password(self.work_name)
        if not self.work_name:
            # In case only /password was entered for nzbname
            self.work_name = filename
        self.final_name = self.work_name

        # Check for password also in filename
        if not self.password:
            _, self.password = scan_password(os.path.splitext(filename)[0])

        # Determine category and find pp/script values based on input
        # Later will be re-evaluated based on import steps
        if pp is None:
            r = u = d = None
        else:
            r, u, d = pp_to_opts(pp)

        self.set_priority(priority)  # Parse priority of input
        self.repair = r  # True if we want to repair this set
        self.unpack = u  # True if we want to unpack this set
        self.delete = d  # True if we want to delete this set
        self.script = script  # External script for this set
        self.cat = cat  # User-set category

        # Information fields
        self.url = url or filename
        self.groups = []
        self.avg_date = datetime.datetime(1970, 1, 1, 1, 0)
        self.avg_stamp = 0.0  # Avg age in seconds (calculated from avg_age)

        # Bookkeeping values
        self.meta = {}
        self.servercount = {}  # Dict to keep bytes per server
        self.created = False  # dirprefixes + work_name created
        self.direct_unpacker = None  # Holds the DirectUnpacker instance
        self.bytes = 0  # Original bytesize
        self.bytes_downloaded = 0  # Downloaded byte
        self.bytes_tried = 0  # Which bytes did we try
        self.bytes_missing = 0  # Bytes missing
        self.bad_articles = 0  # How many bad (non-recoverable) articles

        self.partable = {}  # Holds one parfile-name for each set
        self.extrapars = {}  # Holds the extra parfile names for all sets
        self.md5packs = {}  # Holds the md5pack for each set (name: hash)
        self.md5of16k = {}  # Holds the md5s of the first-16k of all files in the NZB (hash: name)

        self.files = []  # List of all NZFs
        self.files_table = {}  # Dictionary of NZFs indexed using NZF_ID
        self.renames = {}  # Dictionary of all renamed files

        self.finished_files = []  # List of all finished NZFs

        # The current status of the nzo eg:
        # Queued, Downloading, Repairing, Unpacking, Failed, Complete
        self.status = status
        self.avg_bps_freq = 0
        self.avg_bps_total = 0

        self.first_articles = []
        self.first_articles_count = 0
        self.saved_articles = []

        self.nzo_id = None

        self.futuretype = futuretype
        self.deleted = False
        self.to_be_removed = False
        self.parsed = False
        self.duplicate = False
        self.oversized = False
        self.precheck = False
        self.incomplete = False
        self.unwanted_ext = 0
        self.rating_filtered = 0
        self.reuse = reuse
        if self.status == Status.QUEUED and not reuse:
            self.precheck = cfg.pre_check()
            if self.precheck:
                self.status = Status.CHECKING

        # Store one line responses for filejoin/par2/unrar/unzip here for history display
        self.action_line = ""
        # Store the results from various filejoin/par2/unrar/unzip stages
        self.unpack_info = {}
        # Stores one line containing the last failure
        self.fail_msg = ""
        # Stores various info about the nzo to be
        self.nzo_info = nzo_info or {}

        # Temporary store for custom foldername - needs to be stored because of url fetching
        self.custom_name = nzbname

        self.next_save = None
        self.save_timeout = None
        self.encrypted = 0
        self.url_wait = None
        self.url_tries = 0
        self.pp_active = False  # Signals active post-processing (not saved)
        self.md5sum = None

        if nzb is None and not reuse:
            # This is a slot for a future NZB, ready now
            # It can also be a retry of a failed job with no extra NZB-file
            return

        # Apply conversion option to final folder
        if cfg.replace_spaces():
            logging.info("Replacing spaces with underscores in %s", self.final_name)
            self.final_name = self.final_name.replace(" ", "_")
        if cfg.replace_dots():
            logging.info("Replacing dots with spaces in %s", self.final_name)
            self.final_name = self.final_name.replace(".", " ")

        # Check against identical checksum or series/season/episode
        if (not reuse) and nzb and dup_check and priority != REPAIR_PRIORITY:
            duplicate, series = self.has_duplicates()
        else:
            duplicate = series = 0

        # Reuse the existing directory
        if reuse and os.path.exists(reuse):
            work_dir = long_path(reuse)
        else:
            # Determine "incomplete" folder and trim path on Windows to prevent long-path unrar errors
            work_dir = long_path(os.path.join(cfg.download_dir.get_path(), self.work_name))
            work_dir = trim_win_path(work_dir)
            work_dir = get_unique_path(work_dir, create_dir=True)
            set_permissions(work_dir)

        # Always create the admin-directory, just to be sure
        admin_dir = os.path.join(work_dir, JOB_ADMIN)
        if not os.path.exists(admin_dir):
            os.mkdir(admin_dir)
        _, self.work_name = os.path.split(work_dir)
        self.created = True

        # When doing a retry or repair, remove old cache-files
        if reuse:
            remove_all(admin_dir, "SABnzbd_nz?_*", keep_folder=True)
            remove_all(admin_dir, "SABnzbd_article_*", keep_folder=True)

        if nzb and "<nzb" in nzb:
            try:
                sabnzbd.nzbparser.nzbfile_parser(nzb, self)
            except Exception as err:
                self.incomplete = True
                logging.warning(T("Invalid NZB file %s, skipping (reason=%s, line=%s)"), filename, err, "1")
                logging.info("Traceback: ", exc_info=True)

                # Some people want to keep the broken files
                if cfg.allow_incomplete_nzb():
                    self.pause()
                else:
                    self.purge_data()
                    raise ValueError

            sabnzbd.backup_nzb(filename, nzb)
            sabnzbd.save_compressed(admin_dir, filename, nzb)

        if not self.files and not reuse:
            self.purge_data()
            if cfg.warn_empty_nzb():
                mylog = logging.warning
            else:
                mylog = logging.info
            if self.url:
                mylog(T("Empty NZB file %s") + " [%s]", filename, self.url)
            else:
                mylog(T("Empty NZB file %s"), filename)
            raise ValueError

        if cat is None:
            for metacat in self.meta.get("category", ()):
                metacat = cat_convert(metacat)
                if metacat:
                    cat = metacat
                    break

        if cat is None:
            for grp in self.groups:
                cat = cat_convert(grp)
                if cat:
                    break

        # Pickup backed-up attributes when re-using
        if reuse:
            cat, pp, script, priority = self.load_attribs()

        # Determine category and find pp/script values
        self.cat, pp_tmp, self.script, priority = cat_to_opts(cat, pp, script, priority)
        self.set_priority(priority)
        self.repair, self.unpack, self.delete = pp_to_opts(pp_tmp)

        # Run user pre-queue script if set and valid
        if not reuse and make_script_path(cfg.pre_script()):
            # Call the script
            accept, name, pp, cat_pp, script_pp, priority, group = sabnzbd.newsunpack.pre_queue(self, pp, cat)

            # Accept or reject
            accept = int_conv(accept)
            if accept < 1:
                self.purge_data()
                raise TypeError
            if accept == 2:
                self.fail_msg = T("Pre-queue script marked job as failed")

            # Process all options, only over-write if set by script
            # Beware that cannot do "if priority/pp", because those can
            # also have a valid value of 0, which shouldn't be ignored
            if name:
                self.set_final_name_and_scan_password(name)
            try:
                pp = int(pp)
            except:
                pp = None
            if cat_pp:
                cat = cat_pp
            try:
                priority = int(priority)
            except:
                priority = DEFAULT_PRIORITY
            if script_pp:
                script = script_pp
            if group:
                self.groups = [str(group)]

            # Re-evaluate results from pre-queue script
            self.cat, pp, self.script, priority = cat_to_opts(cat, pp, script, priority)
            self.set_priority(priority)
            self.repair, self.unpack, self.delete = pp_to_opts(pp)
        else:
            accept = 1

        # Pause job when above size limit
        limit = cfg.size_limit.get_int()
        if not reuse and abs(limit) > 0.5 and self.bytes > limit:
            logging.info("Job too large, forcing low prio and paused (%s)", self.final_name)
            self.pause()
            self.oversized = True
            self.priority = LOW_PRIORITY

        if duplicate and ((not series and cfg.no_dupes() == 1) or (series and cfg.no_series_dupes() == 1)):
            if cfg.warn_dupl_jobs():
                logging.warning(T('Ignoring duplicate NZB "%s"'), filename)
            self.purge_data()
            raise TypeError

        if duplicate and ((not series and cfg.no_dupes() == 3) or (series and cfg.no_series_dupes() == 3)):
            if cfg.warn_dupl_jobs():
                logging.warning(T('Failing duplicate NZB "%s"'), filename)
            # Move to history, utilizing the same code as accept&fail from pre-queue script
            self.fail_msg = T("Duplicate NZB")
            accept = 2
            duplicate = False

        if duplicate or self.priority == DUP_PRIORITY:
            if cfg.no_dupes() == 4 or cfg.no_series_dupes() == 4:
                if cfg.warn_dupl_jobs():
                    logging.warning('%s: "%s"', T("Duplicate NZB"), filename)
                self.duplicate = True
                self.priority = NORMAL_PRIORITY
            else:
                if cfg.warn_dupl_jobs():
                    logging.warning(T('Pausing duplicate NZB "%s"'), filename)
                self.duplicate = True
                self.pause()
                self.priority = NORMAL_PRIORITY

        # Check if there is any unwanted extension in plain sight in the NZB itself
        for nzf in self.files:
            if (
                cfg.action_on_unwanted_extensions() >= 1
                and get_ext(nzf.filename).replace(".", "") in cfg.unwanted_extensions()
            ):
                # ... we found an unwanted extension
                logging.warning(T("Unwanted Extension in file %s (%s)"), nzf.filename, self.final_name)
                # Pause, or Abort:
                if cfg.action_on_unwanted_extensions() == 1:
                    logging.debug("Unwanted extension ... pausing")
                    self.unwanted_ext = 1
                    self.pause()
                if cfg.action_on_unwanted_extensions() == 2:
                    logging.debug("Unwanted extension ... aborting")
                    self.fail_msg = T("Aborted, unwanted extension detected")
                    accept = 2

        if self.priority == PAUSED_PRIORITY:
            self.pause()
            self.priority = NORMAL_PRIORITY

        if reuse:
            self.check_existing_files(work_dir)

        if cfg.auto_sort():
            self.files.sort(key=functools.cmp_to_key(nzf_cmp_date))
        else:
            self.files.sort(key=functools.cmp_to_key(nzf_cmp_name))

        # Copy meta fields to nzo_info, if not already set
        for kw in self.meta:
            if not self.nzo_info.get(kw):
                self.nzo_info[kw] = self.meta[kw][0]

        # Show first meta-password (if any), when there's no explicit password
        if not self.password and self.meta.get("password"):
            self.password = self.meta.get("password", [None])[0]

        # Set nzo save-delay to minimum 120 seconds
        self.save_timeout = max(120, min(6.0 * float(self.bytes) / GIGI, 300.0))

        # In case pre-queue script or duplicate check want to move
        # to history we first need an nzo_id by entering the NzbQueue
        if accept == 2:
            self.deleted = True
            self.status = Status.FAILED
            sabnzbd.NzbQueue.do.add(self, quiet=True)
            sabnzbd.NzbQueue.do.end_job(self)
            # Raise error, so it's not added
            raise TypeError