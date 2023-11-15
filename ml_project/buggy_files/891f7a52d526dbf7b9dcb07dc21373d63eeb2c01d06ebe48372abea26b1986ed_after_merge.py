    def add_blob_request(self, blob_request):
        if self._blob_download_request is None:
            d = self.add_request(blob_request)
            self._blob_download_request = blob_request
            blob_request.finished_deferred.addCallbacks(self._downloading_finished,
                                                        self._handle_response_error)
            return d
        else:
            return defer.fail(ValueError("There is already a blob download request active"))