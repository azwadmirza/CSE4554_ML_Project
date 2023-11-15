    def _request(self, method='get', params=None, data=None, files=None, cookies=None):

        if time.time() > self.last_time + 1800 or not self.auth:
            self.last_time = time.time()
            self._get_auth()

        text_params = str(params)
        text_data = str(data)
        text_files = str(files)
        log.debug(
            '{name}: Requested a {method} connection to {url} with'
            ' params: {params} Data: {data} Files: {files}', {
                'name': self.name,
                'method': method.upper(),
                'url': self.url,
                'params': text_params[0:99] + '...' if len(text_params) > 102 else text_params,
                'data': text_data[0:99] + '...' if len(text_data) > 102 else text_data,
                'files': text_files[0:99] + '...' if len(text_files) > 102 else text_files,
            }
        )

        if not self.auth:
            log.warning('{name}: Authentication Failed', {'name': self.name})

            return False
        try:
            self.response = self.session.request(method, self.url, params=params, data=data, files=files,
                                                 cookies=cookies, timeout=120, verify=False)
        except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL) as error:
            log.warning('{name}: Invalid Host: {error}', {'name': self.name, 'error': error})
            return False
        except requests.exceptions.RequestException as error:
            log.warning('{name}: Error occurred during request: {error}',
                        {'name': self.name, 'error': error})
            return False
        except Exception as error:
            log.error('{name}: Unknown exception raised when sending torrent to'
                      ' {name}: {error}', {'name': self.name, 'error': error})
            return False

        if self.response.status_code == 401:
            log.error('{name}: Invalid Username or Password,'
                      ' check your config', {'name': self.name})
            return False

        code_description = http_code_description(self.response.status_code)

        if code_description is not None:
            log.info('{name}: {code}',
                     {'name': self.name, 'code': code_description})
            return False

        log.debug('{name}: Response to {method} request is {response}', {
            'name': self.name,
            'method': method.upper(),
            'response': self.response.text[0:1024] + '...' if len(self.response.text) > 1027 else self.response.text
        })

        return True