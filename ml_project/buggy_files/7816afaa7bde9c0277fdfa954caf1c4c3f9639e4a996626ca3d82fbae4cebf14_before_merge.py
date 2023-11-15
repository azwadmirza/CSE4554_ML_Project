    def __init__(self, delegeate: IConfigRepository):
        self.delegate = delegeate
        self.cache: Dict[str, Optional[ConfigResult]] = {}