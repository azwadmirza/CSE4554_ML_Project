    def cancel(self):
        self.mode.common.log('CompressThread', 'cancel')

        # Let the Web and ZipWriter objects know that we're canceling compression early
        self.mode.web.cancel_compression = True
        try:
            self.mode.web.zip_writer.cancel_compression = True
        except AttributeError:
            # we never made it as far as creating a ZipWriter object
            pass