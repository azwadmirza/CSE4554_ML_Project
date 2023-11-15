        def _on_create_failure(failure):
            """
            Error callback
            :param failure: from create_torrent_file
            """
            failure.trap(IOError, UnicodeDecodeError, RuntimeError)
            self._logger.exception(failure)
            request.write(return_handled_exception(request, failure.value))
            request.finish()