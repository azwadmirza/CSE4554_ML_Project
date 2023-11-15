def _collect_facts(resource):
    """Transfrom cluster information to dict."""
    facts = {
        'identifier': resource['ClusterIdentifier'],
        'status': resource['ClusterStatus'],
        'username': resource['MasterUsername'],
        'db_name': resource['DBName'],
        'maintenance_window': resource['PreferredMaintenanceWindow'],
        'enhanced_vpc_routing': resource['EnhancedVpcRouting']

    }

    for node in resource['ClusterNodes']:
        if node['NodeRole'] in ('SHARED', 'LEADER'):
            facts['private_ip_address'] = node['PrivateIPAddress']
            if facts['enhanced_vpc_routing'] is False:
                facts['public_ip_address'] = node['PublicIPAddress']
            else:
                facts['public_ip_address'] = None
            break

    # Some parameters are not ready instantly if you don't wait for available
    # cluster status
    facts['create_time'] = None
    facts['url'] = None
    facts['port'] = None
    facts['availability_zone'] = None

    if resource['ClusterStatus'] != "creating":
        facts['create_time'] = resource['ClusterCreateTime']
        facts['url'] = resource['Endpoint']['Address']
        facts['port'] = resource['Endpoint']['Port']
        facts['availability_zone'] = resource['AvailabilityZone']

    return facts