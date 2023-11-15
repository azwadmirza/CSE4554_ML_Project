def local_api(method, endpoint, json_body):
    try:
        url = "http://{}{}".format(RuntimeConfig.JOB_SERVER_HOST, endpoint)
        stat_logger.info('local api request: {}'.format(url))
        action = getattr(requests, method.lower(), None)
        response = action(url=url, json=json_body, headers=HEADERS)
        stat_logger.info(response.text)
        response_json_body = response.json()
        stat_logger.info('local api response: {} {}'.format(endpoint, response_json_body))
        return response_json_body
    except Exception as e:
        raise Exception('local request error: {}'.format(e))