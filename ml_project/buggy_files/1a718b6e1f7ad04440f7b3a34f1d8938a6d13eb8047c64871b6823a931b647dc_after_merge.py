    def render_GET(self, request):
        """
        .. http:get:: /download/(string: infohash)/files

        A GET request to this endpoint returns the file information of a specific download.

            **Example request**:

                .. sourcecode:: none

                    curl -X GET http://localhost:8085/downloads/4344503b7e797ebf31582327a5baae35b11bda01/files

            **Example response**:

            .. sourcecode:: javascript

                {
                    "files": [{
                        "index": 1,
                        "name": "test.txt",
                        "size": 12345,
                        "included": True,
                        "progress": 0.5448
                    }, ...]
                }
        """
        download = self.session.get_download(self.infohash)
        if not download:
            return DownloadExportTorrentEndpoint.return_404(request)

        return json.dumps({"files": self.get_files_info_json(download)})