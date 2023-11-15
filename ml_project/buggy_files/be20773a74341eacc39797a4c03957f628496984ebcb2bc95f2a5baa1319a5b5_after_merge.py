    def __init__(self, translator: NullTranslations) -> None:
        self.registry = SphinxComponentRegistry()
        self.messagelog = []  # type: List[str]
        self.translator = translator
        self.verbosity = 0
        self._warncount = 0
        self.warningiserror = False