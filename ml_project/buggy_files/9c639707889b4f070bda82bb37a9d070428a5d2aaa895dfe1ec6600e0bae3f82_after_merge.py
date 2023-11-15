    def iter_log_events(self, log_group_name, interleaved=True):
        # type: (str, bool) -> Iterator[Dict[str, Any]]
        logs = self._client('logs')
        paginator = logs.get_paginator('filter_log_events')
        pages = paginator.paginate(logGroupName=log_group_name,
                                   interleaved=True)
        try:
            for log_message in self._iter_log_messages(pages):
                yield log_message
        except logs.exceptions.ResourceNotFoundException:
            # If the lambda function exists but has not been invoked yet,
            # it's possible that the log group does not exist and we'll get
            # a ResourceNotFoundException.  If this happens we return instead
            # of propagating an exception back to the user.
            pass