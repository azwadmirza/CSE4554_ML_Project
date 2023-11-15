        def _on_remove_failure(failure):
            """
            Error callback
            :param failure: from remove_download
            """
            self._logger.exception(failure)
            request.write(return_handled_exception(request, failure.value))
            request.finish()