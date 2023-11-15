    def __init__(
        self,
        write: typing.Callable[[str], None],
        do_log: bool,
        do_capture: bool,
        max_capture: int,
    ):
        self.write = write
        self.do_log = do_log
        self.do_capture = do_capture
        self.finished = Lock()
        self.capture = deque(
            maxlen=max_capture
        )  # type: typing.MutableSequence[str]
        self.finished.acquire()