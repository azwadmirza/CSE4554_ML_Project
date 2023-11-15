    def render_PATCH(self, request):
        """
        .. http:patch:: /download/(string: infohash)

        A PATCH request to this endpoint will update a download in Tribler.

        A state parameter can be passed to modify the state of the download. Valid states are "resume"
        (to resume a stopped/paused download), "stop" (to stop a running download) and "recheck"
        (to force a recheck of the hashes of a download).

        Another possible parameter is selected_files which manipulates which files are included in the download.
        The selected_files parameter is an array with the file indices as values.

        The anonymity of a download can be changed at runtime by passing the anon_hops parameter, however, this must
        be the only parameter in this request.

            **Example request**:

                .. sourcecode:: none

                    curl -X PATCH http://localhost:8085/downloads/4344503b7e797ebf31582327a5baae35b11bda01
                    --data "state=resume&selected_files[]=file1.iso&selected_files[]=1"

            **Example response**:

                .. sourcecode:: javascript

                    {"modified": True, "infohash": "4344503b7e797ebf31582327a5baae35b11bda01"}
        """
        download = self.session.get_download(self.infohash)
        if not download:
            return DownloadSpecificEndpoint.return_404(request)

        parameters = http.parse_qs(request.content.read(), 1)

        if len(parameters) > 1 and 'anon_hops' in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.twisted_dumps({"error": "anon_hops must be the only parameter in this request"})
        elif 'anon_hops' in parameters:
            anon_hops = int(parameters['anon_hops'][0])
            deferred = self.session.lm.update_download_hops(download, anon_hops)

            def _on_download_readded(_):
                """
                Success callback
                """
                request.write(json.twisted_dumps({"modified": True,
                                          "infohash": hexlify(download.get_def().get_infohash())}))
                request.finish()

            def _on_download_readd_failure(failure):
                """
                Error callback
                :param failure: from LibtorrentDownloadImp.setup()
                """
                self._logger.exception(failure)
                request.write(return_handled_exception(request, failure.value))
                # If the above request.write failed, the request will have already been finished
                if not request.finished:
                    request.finish()

            deferred.addCallback(_on_download_readded)
            deferred.addErrback(_on_download_readd_failure)
            # As we already checked for len(parameters) > 1, we know there are no other parameters.
            # As such, we can return immediately.
            return NOT_DONE_YET

        if 'selected_files' in parameters:
            selected_files_list = []
            for ind in parameters['selected_files']:
                try:
                    selected_files_list.append(download.tdef.get_files()[int(ind)])
                except IndexError:  # File could not be found
                    request.setResponseCode(http.BAD_REQUEST)
                    return json.twisted_dumps({"error": "index %s out of range" % ind})
            download.set_selected_files(selected_files_list)

        if 'state' in parameters and len(parameters['state']) > 0:
            state = parameters['state'][0]
            if state == "resume":
                download.restart()
            elif state == "stop":
                download.stop()
            elif state == "recheck":
                download.force_recheck()
            elif state == "move_storage":
                dest_dir = parameters['dest_dir'][0]
                if not os.path.exists(dest_dir):
                    return json.twisted_dumps({"error": "Target directory (%s) does not exist" % dest_dir})
                download.move_storage(dest_dir)
                download.checkpoint()
            else:
                request.setResponseCode(http.BAD_REQUEST)
                return json.twisted_dumps({"error": "unknown state parameter"})

        return json.twisted_dumps({"modified": True,
                           "infohash": hexlify(download.get_def().get_infohash())})