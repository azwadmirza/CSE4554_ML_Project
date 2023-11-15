    def open(self, kernel_id):
        self.kernel_id = cast_unicode(kernel_id, 'ascii')
        self.session = Session(config=self.config)
        self.save_on_message = self.on_message
        self.on_message = self.on_first_message