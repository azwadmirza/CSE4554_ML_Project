def resolve_service(service_name, dns_client=client, cache=SERVER_CACHE, clock=time):
    cache_entry = cache.get(service_name, None)
    if cache_entry:
        if all(s.expires > int(clock.time()) for s in cache_entry):
            servers = list(cache_entry)
            defer.returnValue(servers)

    servers = []

    try:
        try:
            answers, _, _ = yield dns_client.lookupService(service_name)
        except DNSNameError:
            defer.returnValue([])

        if (len(answers) == 1
                and answers[0].type == dns.SRV
                and answers[0].payload
                and answers[0].payload.target == dns.Name('.')):
            raise ConnectError("Service %s unavailable" % service_name)

        for answer in answers:
            if answer.type != dns.SRV or not answer.payload:
                continue

            payload = answer.payload

            hosts = yield _get_hosts_for_srv_record(
                dns_client, str(payload.target)
            )

            for (ip, ttl) in hosts:
                host_ttl = min(answer.ttl, ttl)

                servers.append(_Server(
                    host=ip,
                    port=int(payload.port),
                    priority=int(payload.priority),
                    weight=int(payload.weight),
                    expires=int(clock.time()) + host_ttl,
                ))

        servers.sort()
        cache[service_name] = list(servers)
    except DomainError as e:
        # We failed to resolve the name (other than a NameError)
        # Try something in the cache, else rereaise
        cache_entry = cache.get(service_name, None)
        if cache_entry:
            logger.warn(
                "Failed to resolve %r, falling back to cache. %r",
                service_name, e
            )
            servers = list(cache_entry)
        else:
            raise e

    defer.returnValue(servers)