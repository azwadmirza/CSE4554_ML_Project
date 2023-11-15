    def __init__(self, view: sublime.View) -> None:
        super().__init__(view)
        self.reflist = []  # type: List[List[str]]