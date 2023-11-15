    def verify_schema(self, dataset_id, table_id, schema):
        try:
            from googleapiclient.errors import HttpError
        except:
            from apiclient.errors import HttpError

        try:
            return (self.service.tables().get(
                projectId=self.project_id,
                datasetId=dataset_id,
                tableId=table_id
            ).execute()['schema']) == schema

        except HttpError as ex:
            self.process_http_error(ex)