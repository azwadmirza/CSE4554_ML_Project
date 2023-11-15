    def __init__(self, profile='default', hist_file=u'', config=None, **traits):
        """Create a new history accessor.
        
        Parameters
        ----------
        profile : str
          The name of the profile from which to open history.
        hist_file : str
          Path to an SQLite history database stored by IPython. If specified,
          hist_file overrides profile.
        config :
          Config object. hist_file can also be set through this.
        """
        # We need a pointer back to the shell for various tasks.
        super(HistoryAccessor, self).__init__(config=config, **traits)
        # defer setting hist_file from kwarg until after init,
        # otherwise the default kwarg value would clobber any value
        # set by config
        if hist_file:
            self.hist_file = hist_file
        
        if self.hist_file == u'':
            # No one has set the hist_file, yet.
            self.hist_file = self._get_hist_file_name(profile)

        if sqlite3 is None and self.enabled:
            warn("IPython History requires SQLite, your history will not be saved\n")
            self.enabled = False
        
        self.init_db()