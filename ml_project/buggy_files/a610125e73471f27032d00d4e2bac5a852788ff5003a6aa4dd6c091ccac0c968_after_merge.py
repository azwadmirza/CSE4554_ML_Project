    def __init__(self, project_id, dataset_id, reauth=False, verbose=False,
                 private_key=None):
        try:
            from googleapiclient.errors import HttpError
        except:
            from apiclient.errors import HttpError
        self.http_error = HttpError
        self.dataset_id = dataset_id
        super(_Table, self).__init__(project_id, reauth, verbose, private_key)