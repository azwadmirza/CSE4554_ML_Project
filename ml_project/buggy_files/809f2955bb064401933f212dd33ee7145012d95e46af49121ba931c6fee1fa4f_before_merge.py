def _get_manifest_digest(login_server, path, username, password, retry_times=3, retry_interval=5):
    for i in range(0, retry_times):
        errorMessage = None
        try:
            headers = _get_authorization_header(username, password)
            headers.update(_get_manifest_v2_header())
            response = requests.get(
                'https://{}/{}'.format(login_server, path),
                headers=headers
            )

            if response.status_code == 200 and response.headers and 'Docker-Content-Digest' in response.headers:
                return response.headers['Docker-Content-Digest']
            elif response.status_code == 401 or response.status_code == 404:
                raise CLIError(response.text)
            else:
                raise Exception(response.text)
        except CLIError:
            raise
        except Exception as e:  # pylint: disable=broad-except
            errorMessage = str(e)
            logger.debug('Retrying %s with exception %s', i + 1, errorMessage)
            time.sleep(retry_interval)
    if errorMessage:
        raise CLIError(errorMessage)