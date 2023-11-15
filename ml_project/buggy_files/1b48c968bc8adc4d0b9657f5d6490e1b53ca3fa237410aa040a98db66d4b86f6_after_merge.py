def post_dns_record(**kwargs):
    '''
    Creates a DNS record for the given name if the domain is managed with DO.
    '''
    if 'kwargs' in kwargs: # flatten kwargs if called via salt-cloud -f
        f_kwargs = kwargs['kwargs']
        del kwargs['kwargs']
        kwargs.update(f_kwargs)
    mandatory_kwargs = ('dns_domain', 'name', 'record_type', 'record_data')
    for i in mandatory_kwargs:
        if kwargs[i]:
            pass
        else:
            error = '{0}="{1}" ## all mandatory args must be provided: {2}'.format(i, kwargs[i], str(mandatory_kwargs))
            raise salt.exceptions.SaltInvocationError(error)

    domain = query(method='domains', droplet_id=kwargs['dns_domain'])

    if domain:
        result = query(
            method='domains',
            droplet_id=kwargs['dns_domain'],
            command='records',
            args={'type': kwargs['record_type'], 'name': kwargs['name'], 'data': kwargs['record_data']},
            http_method='post'
        )
        return result

    return False