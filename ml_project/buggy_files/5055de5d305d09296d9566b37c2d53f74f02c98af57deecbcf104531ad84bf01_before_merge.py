def record_service_health(api, status):
    data = {
        api: status
    }
    health_url = '%s://%s:%s/health' % (get_service_protocol(), config.LOCALHOST, config.PORT_WEB_UI)
    try:
        requests.put(health_url, data=json.dumps(data))
    except Exception:
        # ignore for now, if the service is not running
        pass