def get_url(_suffix):
    return "http://{}/{}".format(RuntimeConfig.JOB_SERVER_HOST.rstrip('/'), _suffix.lstrip('/'))