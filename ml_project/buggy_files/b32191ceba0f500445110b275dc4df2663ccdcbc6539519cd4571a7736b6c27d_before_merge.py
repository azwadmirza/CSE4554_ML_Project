    def createRequest(self, _op, request, _outgoing_data):
        """Create a new request.

        Args:
             request: const QNetworkRequest & req
             _op: Operation op
             _outgoing_data: QIODevice * outgoingData

        Return:
            A QNetworkReply for directories, None for files.
        """
        path = request.url().toLocalFile()
        if os.path.isdir(path):
            data = dirbrowser_html(path)
            return networkreply.FixedDataNetworkReply(
                request, data, 'text/html', self.parent())