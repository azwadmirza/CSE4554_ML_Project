def _determine_auth(**kwargs):
    '''
    Acquire Azure ARM Credentials
    '''
    if 'profile' in kwargs:
        azure_credentials = __salt__['config.option'](kwargs['profile'])
        kwargs.update(azure_credentials)

    service_principal_creds_kwargs = ['client_id', 'secret', 'tenant']
    user_pass_creds_kwargs = ['username', 'password']

    try:
        if kwargs.get('cloud_environment') and kwargs.get('cloud_environment').startswith('http'):
            cloud_env = get_cloud_from_metadata_endpoint(kwargs['cloud_environment'])
        else:
            cloud_env_module = importlib.import_module('msrestazure.azure_cloud')
            cloud_env = getattr(cloud_env_module, kwargs.get('cloud_environment', 'AZURE_PUBLIC_CLOUD'))
    except (AttributeError, ImportError, MetadataEndpointError):
        raise sys.exit('The Azure cloud environment {0} is not available.'.format(kwargs['cloud_environment']))

    if set(service_principal_creds_kwargs).issubset(kwargs):
        if not (kwargs['client_id'] and kwargs['secret'] and kwargs['tenant']):
            raise SaltInvocationError(
                'The client_id, secret, and tenant parameters must all be '
                'populated if using service principals.'
            )
        else:
            credentials = ServicePrincipalCredentials(kwargs['client_id'],
                                                      kwargs['secret'],
                                                      tenant=kwargs['tenant'],
                                                      cloud_environment=cloud_env)
    elif set(user_pass_creds_kwargs).issubset(kwargs):
        if not (kwargs['username'] and kwargs['password']):
            raise SaltInvocationError(
                'The username and password parameters must both be '
                'populated if using username/password authentication.'
            )
        else:
            credentials = UserPassCredentials(kwargs['username'],
                                              kwargs['password'],
                                              cloud_environment=cloud_env)
    else:
        raise SaltInvocationError(
            'Unable to determine credentials. '
            'A subscription_id with username and password, '
            'or client_id, secret, and tenant or a profile with the '
            'required parameters populated'
        )

    if 'subscription_id' not in kwargs:
        raise SaltInvocationError(
            'A subscription_id must be specified'
        )

    subscription_id = salt.utils.stringutils.to_str(kwargs['subscription_id'])

    return credentials, subscription_id, cloud_env