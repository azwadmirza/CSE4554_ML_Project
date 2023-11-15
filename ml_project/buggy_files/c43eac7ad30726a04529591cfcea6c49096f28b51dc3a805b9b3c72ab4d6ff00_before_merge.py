    def cancel(self):
        self.mode.common.log('CompressThread', 'cancel')

        # Let the Web and ZipWriter objects know that we're canceling compression early
        self.mode.web.cancel_compression = True
        if self.mode.web.zip_writer:
            self.mode.web.zip_writer.cancel_compression = True