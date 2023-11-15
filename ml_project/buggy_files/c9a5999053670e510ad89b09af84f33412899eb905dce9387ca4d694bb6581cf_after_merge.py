def _obtain_data_from_registry(login_server,
                               path,
                               username,
                               password,
                               result_index,
                               retry_times=3,
                               retry_interval=5,
                               pagination=20):
    resultList = []
    executeNextHttpCall = True

    while executeNextHttpCall:
        executeNextHttpCall = False
        for i in range(0, retry_times):
            errorMessage = None
            try:
                response = requests.get(
                    'https://{}{}'.format(login_server, path),
                    headers=_get_authorization_header(username, password),
                    params=_get_pagination_params(pagination)
                )
                log_registry_response(response)

                if response.status_code == 200:
                    result = response.json()[result_index]
                    if result:
                        resultList += response.json()[result_index]
                    if 'link' in response.headers and response.headers['link']:
                        linkHeader = response.headers['link']
                        # The registry is telling us there's more items in the list,
                        # and another call is needed. The link header looks something
                        # like `Link: </v2/_catalog?last=hello-world&n=1>; rel="next"`
                        # we should follow the next path indicated in the link header
                        path = linkHeader[(linkHeader.index('<') + 1):linkHeader.index('>')]
                        executeNextHttpCall = True
                    break
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

    return resultList