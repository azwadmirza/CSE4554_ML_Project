    def get_service_instances(config):
        instances = []
        for services in config[CONFIG_CATEGORY_SERVICES]:
            if CONFIG_SERVICE_INSTANCE in config[CONFIG_CATEGORY_SERVICES][services]:
                instance = config[CONFIG_CATEGORY_SERVICES][services][CONFIG_SERVICE_INSTANCE]
                if isinstance(instance, list):
                    for i in instance:
                        instances.append(i)
                else:
                    instances.append(instance)
        return instances