    def __init__(self, name, services, client, networks=None, volumes=None, config_version=None,
                 parallel_limit=None):
        self.name = name
        self.services = services
        self.client = client
        self.volumes = volumes or ProjectVolumes({})
        self.networks = networks or ProjectNetworks({}, False)
        self.config_version = config_version
        parallel.GlobalLimit.set_global_limit(value=parallel_limit)