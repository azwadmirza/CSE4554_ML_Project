    def __init__(self, delegate: IConfigRepository):
        self.delegate = delegate
        self.cache: Dict[str, Optional[ConfigResult]] = {}