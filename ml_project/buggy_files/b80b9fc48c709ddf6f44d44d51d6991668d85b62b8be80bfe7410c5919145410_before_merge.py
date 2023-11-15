    def get_willow_image(self):
        # Open file if it is closed
        close_file = False
        try:
            if self.file.closed:
                self.file.open('rb')
                close_file = True
        except IOError as e:
            # re-throw this as a SourceImageIOError so that calling code can distinguish
            # these from IOErrors elsewhere in the process
            raise SourceImageIOError(text_type(e))

        # Seek to beginning
        self.file.seek(0)

        try:
            yield WillowImage.open(self.file)
        finally:
            if close_file:
                self.file.close()