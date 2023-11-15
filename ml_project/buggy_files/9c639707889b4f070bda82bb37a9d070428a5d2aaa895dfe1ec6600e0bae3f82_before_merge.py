    def iter_log_events(self, log_group_name, interleaved=True):
        # type: (str, bool) -> Iterator[Dict[str, Any]]
        logs = self._client('logs')
        paginator = logs.get_paginator('filter_log_events')
        for page in paginator.paginate(logGroupName=log_group_name,
                                       interleaved=True):
            events = page['events']
            for event in events:
                # timestamp is modeled as a 'long', so we'll
                # convert to a datetime to make it easier to use
                # in python.
                event['ingestionTime'] = self._convert_to_datetime(
                    event['ingestionTime'])
                event['timestamp'] = self._convert_to_datetime(
                    event['timestamp'])
                yield event