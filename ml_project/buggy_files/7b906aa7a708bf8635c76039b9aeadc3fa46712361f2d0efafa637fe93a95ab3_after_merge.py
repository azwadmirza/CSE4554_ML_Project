    def __init__(
        self,
        dialect: str,
        *,
        # Is the connection a Daemon?
        daemon: bool = True,
        # Deficiencies to work around:
        safe_indexes: bool = True,
        requires_limit: bool = False
    ) -> None:
        super().__setattr__("_mutable", True)

        self.dialect = dialect
        self.daemon = daemon
        self.requires_limit = requires_limit
        self.safe_indexes = safe_indexes

        super().__setattr__("_mutable", False)