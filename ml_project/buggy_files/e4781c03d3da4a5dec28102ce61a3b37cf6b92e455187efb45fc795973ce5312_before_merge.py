    def _initialize_history(self, hist_file):
        """Initialize history using history related attributes

        This function can determine whether history is saved in the prior text-based
        format (one line of input is stored as one line in the file), or the new-as-
        of-version 0.9.13 pickle based format.

        History created by versions <= 0.9.12 is in readline format, i.e. plain text files.

        Initializing history does not effect history files on disk, versions >= 0.9.13 always
        write history in the pickle format.
        """
        self.history = History()
        # with no persistent history, nothing else in this method is relevant
        if not hist_file:
            self.persistent_history_file = hist_file
            return

        hist_file = os.path.abspath(os.path.expanduser(hist_file))

        # on Windows, trying to open a directory throws a permission
        # error, not a `IsADirectoryError`. So we'll check it ourselves.
        if os.path.isdir(hist_file):
            msg = "Persistent history file '{}' is a directory"
            self.perror(msg.format(hist_file))
            return

        # Create the directory for the history file if it doesn't already exist
        hist_file_dir = os.path.dirname(hist_file)
        try:
            os.makedirs(hist_file_dir, exist_ok=True)
        except OSError as ex:
            msg = "Error creating persistent history file directory '{}': {}".format(hist_file_dir, ex)
            self.pexcept(msg)
            return

        # first we try and unpickle the history file
        history = History()

        try:
            with open(hist_file, 'rb') as fobj:
                history = pickle.load(fobj)
        except (AttributeError, EOFError, FileNotFoundError, ImportError, IndexError, KeyError, pickle.UnpicklingError):
            # If any non-operating system error occurs when attempting to unpickle, just use an empty history
            pass
        except OSError as ex:
            msg = "Can not read persistent history file '{}': {}"
            self.pexcept(msg.format(hist_file, ex))
            return

        self.history = history
        self.history.start_session()
        self.persistent_history_file = hist_file

        # populate readline history
        if rl_type != RlType.NONE:
            last = None
            for item in history:
                # Break the command into its individual lines
                for line in item.raw.splitlines():
                    # readline only adds a single entry for multiple sequential identical lines
                    # so we emulate that behavior here
                    if line != last:
                        readline.add_history(line)
                        last = line

        # register a function to write history at save
        # if the history file is in plain text format from 0.9.12 or lower
        # this will fail, and the history in the plain text file will be lost
        import atexit
        atexit.register(self._persist_history)