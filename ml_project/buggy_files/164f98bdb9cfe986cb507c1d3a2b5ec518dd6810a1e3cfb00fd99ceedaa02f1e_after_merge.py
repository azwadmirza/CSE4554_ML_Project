    def __init__(self, store_dir):
        super(LevelDbStore, self).__init__()

        self._store_dir = store_dir
        self._pending_torrents = {}
        self._logger = logging.getLogger(self.__class__.__name__)
        # This is done to work around LevelDB's inability to deal with non-ascii paths on windows.
        try:
            db_path = store_dir.decode('windows-1252') if sys.platform == "win32" else store_dir
            self._db = self._leveldb(db_path)
        except ValueError:
            # This can happen on Windows when the state dir and Tribler installation are on different disks.
            # In this case, hope for the best by using the full path.
            self._db = self._leveldb(store_dir)
        except Exception as exc:
            # We cannot simply catch LevelDBError since that class might not be available on some systems.
            if use_leveldb and isinstance(exc, LevelDBError):
                # The database might be corrupt, start with a fresh one
                self._logger.error("Corrupt LevelDB store detected; recreating database")
                rmtree(self._store_dir)
                os.makedirs(self._store_dir)
                self._db = self._leveldb(os.path.relpath(store_dir, os.getcwdu()))
            else:  # If something else goes wrong, we throw the exception again
                raise

        self._writeback_lc = self.register_task("flush cache ", LoopingCall(self.flush))
        self._writeback_lc.clock = self._reactor
        self._writeback_lc.start(WRITEBACK_PERIOD)