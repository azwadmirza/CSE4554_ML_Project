def _delete_data_from_registry(login_server, path, username, password, retry_times=3, retry_interval=5):
    for i in range(0, retry_times):
        errorMessage = None
        try:
            response = requests.delete(
                'https://{}/{}'.format(login_server, path),
                headers=_get_authorization_header(username, password)
            )

            if response.status_code == 200 or response.status_code == 202:
                return
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