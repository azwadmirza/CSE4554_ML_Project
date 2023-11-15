    def flush_queued_events(self, retry_count=0):
        """Flush all queued events.

        Returns:
            dict: A dict object that contains the number of events
                that were sent to Elastic as well as information
                on whether there were any errors, and what the
                details of these errors if any.
            retry_count: optional int indicating whether this is a retry.
        """
        if not self.import_events:
            return {}

        return_dict = {
            'number_of_events': len(self.import_events) / 2,
            'total_events': self.import_counter['events'],
        }

        try:
            # pylint: disable=unexpected-keyword-arg
            results = self.client.bulk(
                body=self.import_events, timeout=self._request_timeout)
        except (ConnectionTimeout, socket.timeout):
            if retry_count >= self.DEFAULT_FLUSH_RETRY_LIMIT:
                es_logger.error(
                    'Unable to add events, reached recount max.',
                    exc_info=True)
                return {}

            es_logger.error('Unable to add events (retry {0:d}/{1:d})'.format(
                retry_count, self.DEFAULT_FLUSH_RETRY_LIMIT))
            return self.flush_queued_events(retry_count + 1)

        errors_in_upload = results.get('errors', False)
        return_dict['errors_in_upload'] = errors_in_upload

        if errors_in_upload:
            items = results.get('items', [])
            return_dict['errors'] = []

            es_logger.error('Errors while attempting to upload events.')
            for item in items:
                index = item.get('index', {})
                index_name = index.get('_index', 'N/A')

                _ = self._error_container.setdefault(
                    index_name, {
                        'errors': [],
                        'types': Counter(),
                        'details': Counter()
                    }
                )

                error_counter = self._error_container[index_name]['types']
                error_detail_counter = self._error_container[index_name][
                    'details']
                error_list = self._error_container[index_name]['errors']

                error = index.get('error', {})
                status_code = index.get('status', 0)
                doc_id = index.get('_id', '(unable to get doc id)')
                caused_by = error.get('caused_by', {})

                caused_reason = caused_by.get(
                    'reason', 'Unkown Detailed Reason')

                error_counter[error.get('type')] += 1
                detail_msg = '{0:s}/{1:s}'.format(
                    caused_by.get('type', 'Unknown Detailed Type'),
                    ' '.join(caused_reason.split()[:5])
                )
                error_detail_counter[detail_msg] += 1

                error_msg = '<{0:s}> {1:s} [{2:s}/{3:s}]'.format(
                    error.get('type', 'Unknown Type'),
                    error.get('reason', 'No reason given'),
                    caused_by.get('type', 'Unknown Type'),
                    caused_reason,
                )
                error_list.append(error_msg)
                try:
                    es_logger.error(
                        'Unable to upload document: {0:s} to index {1:s} - '
                        '[{2:d}] {3:s}'.format(
                            doc_id, index_name, status_code, error_msg))
                # We need to catch all exceptions here, since this is a crucial
                # call that we do not want to break operation.
                except Exception:  # pylint: disable=broad-except
                    es_logger.error(
                        'Unable to upload document, and unable to log the '
                        'error itself.', exc_info=True)

        return_dict['error_container'] = self._error_container

        self.import_events = []
        return return_dict