    def render_PATCH(self, request):
        """
        .. http:patch:: /download/(string: infohash)

        A PATCH request to this endpoint will update a download in Tribler.

        A state parameter can be passed to modify the state of the download. Valid states are "resume"
        (to resume a stopped/paused download), "stop" (to stop a running download) and "recheck"
        (to force a recheck of the hashes of a download).

        Another possible parameter is selected_files which manipulates which files are included in the download.
        The selected_files parameter is an array with the file names as values.

        The anonymity of a download can be changed at runtime by passing the anon_hops parameter, however, this must
        be the only parameter in this request.

            **Example request**:

                .. sourcecode:: none

                    curl -X PATCH http://localhost:8085/downloads/4344503b7e797ebf31582327a5baae35b11bda01
                    --data "state=resume&selected_files[]=file1.iso&selected_files[]=file2.iso"

            **Example response**:

                .. sourcecode:: javascript

                    {"modified": True}
        """
        download = self.session.get_download(self.infohash)
        if not download:
            return DownloadSpecificEndpoint.return_404(request)

        parameters = http.parse_qs(request.content.read(), 1)

        if len(parameters) > 1 and 'anon_hops' in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "anon_hops must be the only parameter in this request"})
        elif 'anon_hops' in parameters:
            anon_hops = int(parameters['anon_hops'][0])
            self.session.lm.update_download_hops(download, anon_hops)

        if 'selected_files[]' in parameters:
            selected_files_list = [unicode(f, 'utf-8') for f in parameters['selected_files[]']]
            download.set_selected_files(selected_files_list)

        if 'state' in parameters and len(parameters['state']) > 0:
            state = parameters['state'][0]
            if state == "resume":
                download.restart()
            elif state == "stop":
                download.stop()
            elif state == "recheck":
                download.force_recheck()
            else:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "unknown state parameter"})

        return json.dumps({"modified": True})