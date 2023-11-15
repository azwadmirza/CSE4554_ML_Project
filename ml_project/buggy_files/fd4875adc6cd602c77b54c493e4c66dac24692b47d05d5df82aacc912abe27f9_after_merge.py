    def _get_file_stream(self, total_content_length, content_type, filename=None, content_length=None):
        """
        This gets called for each file that gets uploaded, and returns an file-like
        writable stream.
        """
        if self.upload_request:
            if not self.told_gui_about_request:
                # Tell the GUI about the request
                self.web.add_request(self.web.REQUEST_STARTED, self.path, {
                    'id': self.upload_id,
                    'content_length': self.content_length
                })
                self.web.receive_mode.uploads_in_progress.append(self.upload_id)

                self.told_gui_about_request = True

            self.progress[filename] = {
                'uploaded_bytes': 0,
                'complete': False
            }

        return ReceiveModeTemporaryFile(self, filename, self.file_write_func, self.file_close_func)