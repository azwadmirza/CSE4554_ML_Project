    def __init__(self, use_interactive=None):
        # type: (bool) -> None
        if use_interactive is None:
            use_interactive = sys.stdin.isatty()
        self.use_interactive = use_interactive

        # This member is used to cache the fetched version of the current
        # ``svn`` client.
        # Special value definitions:
        #   None: Not evaluated yet.
        #   Empty tuple: Could not parse version.
        self._vcs_version = None  # type: Optional[Tuple[int, ...]]

        super(Subversion, self).__init__()