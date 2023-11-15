    def load_data(self, dataframe, dataset_id, table_id, chunksize):
        from apiclient.errors import HttpError

        job_id = uuid.uuid4().hex
        rows = []
        remaining_rows = len(dataframe)

        if self.verbose:
            total_rows = remaining_rows
            self._print("\n\n")

        for index, row in dataframe.reset_index(drop=True).iterrows():
            row_dict = dict()
            row_dict['json'] = json.loads(row.to_json(force_ascii=False,
                                                      date_unit='s',
                                                      date_format='iso'))
            row_dict['insertId'] = job_id + str(index)
            rows.append(row_dict)
            remaining_rows -= 1

            if (len(rows) % chunksize == 0) or (remaining_rows == 0):
                self._print("\rStreaming Insert is {0}% Complete".format(
                    ((total_rows - remaining_rows) * 100) / total_rows))

                body = {'rows': rows}

                try:
                    response = self.service.tabledata().insertAll(
                        projectId=self.project_id,
                        datasetId=dataset_id,
                        tableId=table_id,
                        body=body).execute()
                except HttpError as ex:
                    self.process_http_error(ex)

                # For streaming inserts, even if you receive a success HTTP
                # response code, you'll need to check the insertErrors property
                # of the response to determine if the row insertions were
                # successful, because it's possible that BigQuery was only
                # partially successful at inserting the rows.  See the `Success
                # HTTP Response Codes
                # <https://cloud.google.com/bigquery/
                #       streaming-data-into-bigquery#troubleshooting>`__
                # section

                insert_errors = response.get('insertErrors', None)
                if insert_errors:
                    self.process_insert_errors(insert_errors)

                sleep(1)  # Maintains the inserts "per second" rate per API
                rows = []

        self._print("\n")