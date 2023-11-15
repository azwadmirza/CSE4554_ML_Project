        def _on_create_failure(failure):
            """
            Error callback
            :param failure: from create_torrent_file
            """
            failure.trap(IOError, UnicodeDecodeError, RuntimeError)
            self._logger.exception(failure)
            request.write(return_handled_exception(request, failure.value))
            # If the above request.write failed, the request will have already been finished
            if not request.finished:
                request.finish()