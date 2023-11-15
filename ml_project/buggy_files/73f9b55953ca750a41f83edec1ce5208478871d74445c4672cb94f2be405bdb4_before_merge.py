    def __init__(self, db_filename, channels_dir, my_key, disable_sync=False):
        self.db_filename = db_filename
        self.channels_dir = channels_dir
        self.my_key = my_key
        self._logger = logging.getLogger(self.__class__.__name__)

        self._shutting_down = False
        self.batch_size = 10  # reasonable number, a little bit more than typically fits in a single UDP packet
        self.reference_timedelta = timedelta(milliseconds=100)
        self.sleep_on_external_thread = 0.05  # sleep this amount of seconds between batches executed on external thread

        create_db = (db_filename == ":memory:" or not os.path.isfile(self.db_filename))

        # We have to dynamically define/init ORM-managed entities here to be able to support
        # multiple sessions in Tribler. ORM-managed classes are bound to the database instance
        # at definition.
        self._db = orm.Database()

        # Possibly disable disk sync.
        # !!! ACHTUNG !!! This should be used only for special cases (e.g. DB upgrades), because
        # losing power during a write will corrupt the database.
        if disable_sync:

            # This attribute is internally called by Pony on startup, though pylint cannot detect it
            # with the static analysis.
            # pylint: disable=unused-variable
            @self._db.on_connect(provider='sqlite')
            def sqlite_disable_sync(_, connection):
                cursor = connection.cursor()
                cursor.execute("PRAGMA synchronous = 0")
            # pylint: enable=unused-variable

        self.MiscData = misc.define_binding(self._db)

        self.TrackerState = tracker_state.define_binding(self._db)
        self.TorrentState = torrent_state.define_binding(self._db)

        self.clock = DiscreteClock(None if db_filename == ":memory:" else self.MiscData)

        self.ChannelNode = channel_node.define_binding(self._db, logger=self._logger, key=my_key, clock=self.clock)
        self.TorrentMetadata = torrent_metadata.define_binding(self._db)
        self.ChannelMetadata = channel_metadata.define_binding(self._db)

        self.ChannelMetadata._channels_dir = channels_dir

        self._db.bind(provider='sqlite', filename=db_filename, create_db=create_db)
        if create_db:
            with db_session:
                self._db.execute(sql_create_fts_table)
        self._db.generate_mapping(create_tables=create_db)  # Must be run out of session scope
        if create_db:
            with db_session:
                self._db.execute(sql_add_fts_trigger_insert)
                self._db.execute(sql_add_fts_trigger_delete)
                self._db.execute(sql_add_fts_trigger_update)
                self._db.execute(sql_add_signature_index)
                self._db.execute(sql_add_public_key_index)
                self._db.execute(sql_add_infohash_index)

        if create_db:
            with db_session:
                self.MiscData(name="db_version", value="0")

        self.clock.init_clock()