    def close(self):
        """
        Closing the request.
        """
        super(ReceiveModeRequest, self).close()

        # Prevent calling this method more than once per request
        if self.closed:
            return
        self.closed = True

        self.web.common.log('ReceiveModeRequest', 'close')

        try:
            if self.told_gui_about_request:
                upload_id = self.upload_id

                if not self.web.stop_q.empty():
                    # Inform the GUI that the upload has canceled
                    self.web.add_request(self.web.REQUEST_UPLOAD_CANCELED, self.path, {
                        'id': upload_id
                    })
                else:
                    # Inform the GUI that the upload has finished
                    self.web.add_request(self.web.REQUEST_UPLOAD_FINISHED, self.path, {
                        'id': upload_id
                    })
                self.web.receive_mode.uploads_in_progress.remove(upload_id)

        except AttributeError:
            pass