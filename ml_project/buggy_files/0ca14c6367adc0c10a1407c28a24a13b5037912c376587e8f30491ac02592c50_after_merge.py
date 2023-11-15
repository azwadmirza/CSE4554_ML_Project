    def render_DELETE(self, request):
        """
        .. http:delete:: /downloads/(string: infohash)

        A DELETE request to this endpoint removes a specific download from Tribler. You can specify whether you only
        want to remove the download or the download and the downloaded data using the remove_data parameter.

            **Example request**:

                .. sourcecode:: none

                    curl -X DELETE http://localhost:8085/download/4344503b7e797ebf31582327a5baae35b11bda01
                    --data "remove_data=1"

            **Example response**:

                .. sourcecode:: javascript

                    {"removed": True}
        """
        parameters = http.parse_qs(request.content.read(), 1)

        if 'remove_data' not in parameters or len(parameters['remove_data']) == 0:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "remove_data parameter missing"})

        download = self.session.get_download(self.infohash)
        if not download:
            return DownloadSpecificEndpoint.return_404(request)

        remove_data = parameters['remove_data'][0] == "1"

        def _on_torrent_removed(_):
            """
            Success callback
            """
            request.write(json.dumps({"removed": True}))
            request.finish()

        def _on_remove_failure(failure):
            """
            Error callback
            :param failure: from remove_download
            """
            self._logger.exception(failure)
            request.write(return_handled_exception(request, failure.value))
            # If the above request.write failed, the request will have already been finished
            if not request.finished:
                request.finish()

        deferred = self.session.remove_download(download, remove_content=remove_data)
        deferred.addCallback(_on_torrent_removed)
        deferred.addErrback(_on_remove_failure)

        return NOT_DONE_YET