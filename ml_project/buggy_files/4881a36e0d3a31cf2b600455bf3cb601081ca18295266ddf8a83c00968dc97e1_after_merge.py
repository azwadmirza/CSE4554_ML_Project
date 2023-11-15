    def init_config(**kwargs):
        for k, v in kwargs.items():
            if hasattr(RuntimeConfig, k):
                setattr(RuntimeConfig, k, v)
                if k == 'HTTP_PORT':
                    setattr(RuntimeConfig, 'JOB_SERVER_HOST', "{}:{}".format(get_lan_ip(), RuntimeConfig.HTTP_PORT))