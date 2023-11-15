    def __init__(self, fobj):
        self.md5 = hashlib.md5()
        self.is_text_file = None
        self.reader = fobj.read1 if hasattr(fobj, "read1") else fobj.read