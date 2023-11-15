    def download_nzb_for_post(self, result):
        """
        Download the nzb content, prior to sending it to the nzb download client.

        :param result: Nzb SearchResult object.
        :return: The content of the nzb file if successful else None.
        """
        if not self.login():
            return False

        # For now to separate the url and the post data, where splitting it with a pipe.
        url, data = result.url.split('|')

        data = {
            data.split('=')[1]: 'on',
            'action': 'nzb'
        }

        log.info('Downloading {result} from {provider} at {url} and data {data}',
                 {'result': result.name, 'provider': self.name, 'url': result.url, 'data': data})

        verify = False if self.public else None

        result = self.session.post(url, data=data, headers=self.session.headers,
                                   verify=verify, hooks={}, allow_redirects=True).content

        # Validate that the result has the content of a valid nzb.
        if not BinSearchProvider.nzb_check_segment.search(result):
            log.info('Result returned from BinSearch was not a valid nzb')
            return None

        return result