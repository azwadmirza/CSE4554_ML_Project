    def __init__(self) -> None:
        self.registry = SphinxComponentRegistry()
        self.messagelog = []  # type: List[str]
        self.translator = None
        self.verbosity = 0
        self._warncount = 0
        self.warningiserror = False