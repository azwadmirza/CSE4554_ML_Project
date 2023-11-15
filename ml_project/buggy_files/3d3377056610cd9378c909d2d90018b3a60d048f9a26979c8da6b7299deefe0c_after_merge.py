    def load(self, filename, max_age=0):
        self.filename = filename
        self.data = {}
        try:
            if max_age > 0:
                st = os.stat(self.filename)
                if st.st_mtime + max_age < time.clock():
                    self.save()
            with codecs_open(self.filename, 'r', encoding=self._encoding) as f:
                self.data = json.load(f)
        except (OSError, IOError, t_JSONDecodeError):
            get_logger(__name__).warning("Fail to load or parse file %s. It is overridden by default settings.",
                                         self.filename)
            self.save()