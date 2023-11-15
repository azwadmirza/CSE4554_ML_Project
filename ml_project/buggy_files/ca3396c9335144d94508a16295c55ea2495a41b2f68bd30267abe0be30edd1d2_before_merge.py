        def handle(domain):
            domain = domain['DomainName']
            if re.match(filter, domain):
                details = cmd_es('describe-elasticsearch-domain --domain-name %s' % domain, env)
                details = json.loads(details)['DomainStatus']
                arn = details['ARN']
                es = ElasticSearch(arn)
                es.endpoint = details['Endpoint']
                result.append(es)
                pool[arn] = es