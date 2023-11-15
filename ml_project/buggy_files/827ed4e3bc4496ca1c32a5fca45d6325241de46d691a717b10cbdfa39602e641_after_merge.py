    def __init__(self, view: sublime.View) -> None:
        super().__init__(view)
        self.reflist = []  # type: List[List[str]]
        self.word_region = None  # type: Optional[sublime.Region]
        self.word = ""
        self.base_dir = None  # type: Optional[str]