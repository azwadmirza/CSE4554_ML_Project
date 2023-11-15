def get_elasticsearch_domains(filter='.*', pool={}, env=None):
    result = []
    try:
        out = cmd_es('list-domain-names', env)
        out = json.loads(out)

        def handle(domain):
            domain = domain['DomainName']
            if re.match(filter, domain):
                details = cmd_es('describe-elasticsearch-domain --domain-name %s' % domain, env)
                details = json.loads(details)['DomainStatus']
                arn = details['ARN']
                es = ElasticSearch(arn)
                es.endpoint = details.get('Endpoint', 'n/a')
                result.append(es)
                pool[arn] = es
        parallelize(handle, out['DomainNames'])
    except socket.error:
        pass

    return result