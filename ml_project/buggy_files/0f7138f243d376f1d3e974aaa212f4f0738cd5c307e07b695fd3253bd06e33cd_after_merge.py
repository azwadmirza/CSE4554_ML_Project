    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self._meta = {}
        self.csv_kwargs = kwargs
        self.names = self.csv_kwargs.get("names", None)
        # CSV reader needs a list of files
        # (Assume flat directory structure if this is a dir)
        if len(self.paths) == 1 and self.fs.isdir(self.paths[0]):
            self.paths = self.fs.glob(self.fs.sep.join([self.paths[0], "*"]))