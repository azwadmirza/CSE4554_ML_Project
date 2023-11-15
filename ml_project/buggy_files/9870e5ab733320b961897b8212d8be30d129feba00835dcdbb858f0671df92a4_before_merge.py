    def run_query(self, query):
        from apiclient.errors import HttpError
        from oauth2client.client import AccessTokenRefreshError

        _check_google_client_version()

        job_collection = self.service.jobs()
        job_data = {
            'configuration': {
                'query': {
                    'query': query
                    # 'allowLargeResults', 'createDisposition',
                    # 'preserveNulls', destinationTable, useQueryCache
                }
            }
        }

        self._start_timer()
        try:
            self._print('Requesting query... ', end="")
            query_reply = job_collection.insert(
                projectId=self.project_id, body=job_data).execute()
            self._print('ok.\nQuery running...')
        except (AccessTokenRefreshError, ValueError):
            if self.private_key:
                raise AccessDenied(
                    "The service account credentials are not valid")
            else:
                raise AccessDenied(
                    "The credentials have been revoked or expired, "
                    "please re-run the application to re-authorize")
        except HttpError as ex:
            self.process_http_error(ex)

        job_reference = query_reply['jobReference']

        while not query_reply.get('jobComplete', False):
            self.print_elapsed_seconds('  Elapsed', 's. Waiting...')
            try:
                query_reply = job_collection.getQueryResults(
                    projectId=job_reference['projectId'],
                    jobId=job_reference['jobId']).execute()
            except HttpError as ex:
                self.process_http_error(ex)

        if self.verbose:
            if query_reply['cacheHit']:
                self._print('Query done.\nCache hit.\n')
            else:
                bytes_processed = int(query_reply.get(
                    'totalBytesProcessed', '0'))
                self._print('Query done.\nProcessed: {}\n'.format(
                    self.sizeof_fmt(bytes_processed)))

            self._print('Retrieving results...')

        total_rows = int(query_reply['totalRows'])
        result_pages = list()
        seen_page_tokens = list()
        current_row = 0
        # Only read schema on first page
        schema = query_reply['schema']

        # Loop through each page of data
        while 'rows' in query_reply and current_row < total_rows:
            page = query_reply['rows']
            result_pages.append(page)
            current_row += len(page)

            self.print_elapsed_seconds(
                '  Got page: {}; {}% done. Elapsed'.format(
                    len(result_pages),
                    round(100.0 * current_row / total_rows)))

            if current_row == total_rows:
                break

            page_token = query_reply.get('pageToken', None)

            if not page_token and current_row < total_rows:
                raise InvalidPageToken("Required pageToken was missing. "
                                       "Received {0} of {1} rows"
                                       .format(current_row, total_rows))

            elif page_token in seen_page_tokens:
                raise InvalidPageToken("A duplicate pageToken was returned")

            seen_page_tokens.append(page_token)

            try:
                query_reply = job_collection.getQueryResults(
                    projectId=job_reference['projectId'],
                    jobId=job_reference['jobId'],
                    pageToken=page_token).execute()
            except HttpError as ex:
                self.process_http_error(ex)

        if current_row < total_rows:
            raise InvalidPageToken()

        # print basic query stats
        self._print('Got {} rows.\n'.format(total_rows))

        return schema, result_pages