    def start(self, root):
        self.root = root
        logdir = expanduser(config.get('journaldir') or config.default_journal_dir)  # type: ignore # config is weird

        if not logdir or not isdir(logdir):  # type: ignore # config does weird things in its get
            self.stop()
            return False

        if self.currentdir and self.currentdir != logdir:
            self.stop()
        self.currentdir = logdir

        # Latest pre-existing logfile - e.g. if E:D is already running. Assumes logs sort alphabetically.
        # Do this before setting up the observer in case the journal directory has gone away
        try:
            logfiles = sorted([x for x in listdir(self.currentdir) if re.search('^Journal(Beta)?\.[0-9]{12}\.[0-9]{2}\.log$', x)],
                              key=lambda x: x.split('.')[1:])
            self.logfile = logfiles and join(self.currentdir, logfiles[-1]) or None
        except:
            self.logfile = None
            return False

        # Set up a watchdog observer.
        # File system events are unreliable/non-existent over network drives on Linux.
        # We can't easily tell whether a path points to a network drive, so assume
        # any non-standard logdir might be on a network drive and poll instead.
        polling = bool(config.get('journaldir')) and platform != 'win32'
        if not polling and not self.observer:
            self.observer = Observer()
            self.observer.daemon = True
            self.observer.start()
        elif polling and self.observer:
            self.observer.stop()
            self.observer = None

        if not self.observed and not polling:
            self.observed = self.observer.schedule(self, self.currentdir)

        if __debug__:
            print('%s Journal "%s"' % (polling and 'Polling' or 'Monitoring', self.currentdir))
            print('Start logfile "%s"' % self.logfile)

        if not self.running():
            self.thread = threading.Thread(target = self.worker, name = 'Journal worker')
            self.thread.daemon = True
            self.thread.start()

        return True