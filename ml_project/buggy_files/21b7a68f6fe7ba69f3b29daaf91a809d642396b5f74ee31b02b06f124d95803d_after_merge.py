    def __init__(self, fobj):
        self.fobj = fobj
        self.md5 = hashlib.md5()
        self.is_text_file = None
        super().__init__()