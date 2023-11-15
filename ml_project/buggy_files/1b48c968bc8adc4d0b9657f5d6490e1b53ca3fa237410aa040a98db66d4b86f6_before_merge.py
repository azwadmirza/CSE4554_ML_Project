def post_dns_record(dns_domain, name, record_type, record_data):
    '''
    Creates or updates a DNS record for the given name if the domain is managed with DO.
    '''
    domain = query(method='domains', droplet_id=dns_domain)

    if domain:
        result = query(
            method='domains',
            droplet_id=dns_domain,
            command='records',
            args={'type': record_type, 'name': name, 'data': record_data},
            http_method='post'
        )
        return result

    return False