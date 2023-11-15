    def download_result(self, result):
        """
        Download result from provider.

        This is used when a blackhole is used for sending the nzb file to the nzb client.
        For now the url and the post data is stored as one string in the db, using a pipe (|) to separate them.

        :param result: A SearchResult object.
        :return: The result of the nzb download (True/False).
        """
        if not self.login():
            return False

        result_name = sanitize_filename(result.name)
        filename = join(self._get_storage_dir(), result_name + '.' + self.provider_type)

        if result.url.startswith('http'):
            self.session.headers.update({
                'Referer': '/'.join(result.url.split('/')[:3]) + '/'
            })

        log.info('Downloading {result} from {provider} at {url}',
                 {'result': result.name, 'provider': self.name, 'url': result.url})

        verify = False if self.public else None

        url, data = result.url.split('|')

        data = {
            data.split('=')[1]: 'on',
            'action': 'nzb',
        }

        if download_file(url, filename, method='POST', data=data, session=self.session,
                         headers=self.headers, verify=verify):

            if self._verify_download(filename):
                log.info('Saved {result} to {location}',
                         {'result': result.name, 'location': filename})
                return True

        return False