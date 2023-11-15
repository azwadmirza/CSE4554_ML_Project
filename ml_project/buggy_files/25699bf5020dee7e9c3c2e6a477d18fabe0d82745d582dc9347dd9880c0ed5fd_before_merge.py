    def open(self, kernel_id):
        self.kernel_id = kernel_id.decode('ascii')
        self.session = Session(config=self.config)
        self.save_on_message = self.on_message
        self.on_message = self.on_first_message