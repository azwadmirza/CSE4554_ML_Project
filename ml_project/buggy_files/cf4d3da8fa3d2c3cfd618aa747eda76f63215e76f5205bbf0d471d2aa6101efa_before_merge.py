def local_api(method, endpoint, json_body):
    try:
        stat_logger.info('local api request: {}'.format(endpoint))
        url = "{}{}".format(SERVER_HOST_URL, endpoint)
        action = getattr(requests, method.lower(), None)
        response = action(url=url, json=json_body, headers=HEADERS)
        stat_logger.info(response.text)
        response_json_body = response.json()
        stat_logger.info('local api response: {} {}'.format(endpoint, response_json_body))
        return response_json_body
    except Exception as e:
        raise Exception('local request error: {}'.format(e))