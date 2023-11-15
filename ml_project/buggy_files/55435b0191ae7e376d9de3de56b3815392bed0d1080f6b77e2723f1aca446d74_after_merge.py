    def touch_or_create(self):
        try:
            self.touch()
        except MissingOutputException:
            # first create directory if it does not yet exist
            dir = self.file if self.is_directory else os.path.dirname(self.file)
            if dir:
                os.makedirs(dir, exist_ok=True)
            # create empty file
            file = (
                os.path.join(self.file, TIMESTAMP_FILENAME)
                if self.is_directory
                else self.file
            )
            with open(file, "w") as f:
                pass