def start_elasticsearch_instance():
    # Note: keep imports here to avoid circular dependencies
    from localstack.services.es import es_starter
    from localstack.services.infra import check_infra, Plugin

    api_name = 'elasticsearch'
    plugin = Plugin(api_name, start=es_starter.start_elasticsearch, check=es_starter.check_elasticsearch)
    t1 = plugin.start(asynchronous=True)
    # sleep some time to give Elasticsearch enough time to come up
    time.sleep(8)
    apis = [api_name]
    # ensure that all infra components are up and running
    check_infra(apis=apis, additional_checks=[es_starter.check_elasticsearch])
    return t1