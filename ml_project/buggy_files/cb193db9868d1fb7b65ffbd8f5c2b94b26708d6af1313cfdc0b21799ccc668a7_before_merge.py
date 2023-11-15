    def __init__(self, project_id, reauth=False, verbose=False,
                 private_key=None):
        from apiclient.errors import HttpError
        self.http_error = HttpError
        super(_Dataset, self).__init__(project_id, reauth, verbose,
                                       private_key)