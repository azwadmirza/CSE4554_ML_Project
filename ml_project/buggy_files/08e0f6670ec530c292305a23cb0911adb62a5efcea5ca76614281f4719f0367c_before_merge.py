    def close(self):
        """
        Closing the request.
        """
        super(ReceiveModeRequest, self).close()
        try:
            if self.told_gui_about_request:
                upload_id = self.upload_id
                # Inform the GUI that the upload has finished
                self.web.add_request(self.web.REQUEST_UPLOAD_FINISHED, self.path, {
                    'id': upload_id
                })
                self.web.receive_mode.uploads_in_progress.remove(upload_id)
        except AttributeError:
            pass