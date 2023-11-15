    def get_service_instances(config):
        instances = []
        for services in config[CONFIG_CATEGORY_SERVICES]:
            if CONFIG_SERVICE_INSTANCE in config[CONFIG_CATEGORY_SERVICES][services]:
                instances.append(config[CONFIG_CATEGORY_SERVICES][services][CONFIG_SERVICE_INSTANCE])
        return instances