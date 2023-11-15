def azure_connect_service(service, credentials, region_name=None):
    try:
        if service == 'storageaccounts':
            return StorageManagementClient(credentials.credentials, credentials.subscription_id)
        elif service == 'monitor':
            return MonitorManagementClient(credentials.credentials, credentials.subscription_id)
        elif service == 'sqldatabase':
            return SqlManagementClient(credentials.credentials, credentials.subscription_id)
        elif service == 'keyvault':
            return KeyVaultManagementClient(credentials.credentials, credentials.subscription_id)
        elif service == 'appgateway':
            return NetworkManagementClient(credentials.credentials, credentials.subscription_id)
        elif service == 'rediscache':
            return RedisManagementClient(credentials.credentials, credentials.subscription_id)
        elif service == 'securitycenter':
            return SecurityCenter(credentials.credentials, credentials.subscription_id, '')
        elif service == 'loadbalancer':
            return NetworkManagementClient(credentials.credentials, credentials.subscription_id)
        else:
            printException('Service %s not supported' % service)
            return None

    except Exception as e:
        printException(e)
        return None