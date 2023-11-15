    def __init__(self, session, tdef):
        super(LibtorrentDownloadImpl, self).__init__()

        self._logger = logging.getLogger(self.__class__.__name__)

        self.dllock = NoDispersyRLock()
        self.session = session
        self.tdef = tdef
        self.handle = None
        self.vod_index = None

        # Just enough so error saving and get_state() works
        self.error = None
        # To be able to return the progress of a stopped torrent, how far it got.
        self.progressbeforestop = 0.0
        self.filepieceranges = []

        # Libtorrent session manager, can be None at this point as the core could have
        # not been started. Will set in create_engine wrapper
        self.ltmgr = None

        # Libtorrent status
        self.dlstates = [DLSTATUS_WAITING4HASHCHECK, DLSTATUS_HASHCHECKING, DLSTATUS_METADATA, DLSTATUS_DOWNLOADING,
                         DLSTATUS_SEEDING, DLSTATUS_SEEDING, DLSTATUS_ALLOCATING_DISKSPACE, DLSTATUS_HASHCHECKING]
        self.dlstate = DLSTATUS_WAITING4HASHCHECK
        self.length = 0
        self.progress = 0.0
        self.curspeeds = {DOWNLOAD: 0.0, UPLOAD: 0.0}  # bytes/s
        self.all_time_upload = 0.0
        self.all_time_download = 0.0
        self.all_time_ratio = 0.0
        self.finished_time = 0.0
        self.done = False
        self.pause_after_next_hashcheck = False
        self.checkpoint_after_next_hashcheck = False
        self.tracker_status = {}  # {url: [num_peers, status_str]}

        self.prebuffsize = 5 * 1024 * 1024
        self.endbuffsize = 0
        self.vod_seekpos = 0

        self.max_prebuffsize = 5 * 1024 * 1024

        self.pstate_for_restart = None

        self.cew_scheduled = False
        self.askmoreinfo = False

        self.correctedinfoname = u""
        self._checkpoint_disabled = False

        self.deferreds_resume = []
        self.deferreds_handle = []

        self.handle_check_lc = self.register_task("handle_check", LoopingCall(self.check_handle))