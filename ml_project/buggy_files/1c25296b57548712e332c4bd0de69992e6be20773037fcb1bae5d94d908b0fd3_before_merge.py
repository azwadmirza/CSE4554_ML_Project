def load_gke_clusters(neo4j_session, gke_list, project_id, gcp_update_tag):
    """
    Ingest GCP GKE Clusters to Neo4j

    :type neo4j_session: Neo4j session object
    :param neo4j session: The Neo4j session object

    :type gke_list: list
    :param gke_list: List of GCP GKE Clusters to inject

    :type gcp_update_tag: timestamp
    :param gcp_update_tag: The timestamp value to set our new Neo4j nodes with

    :rtype: NoneType
    :return: Nothing
    """

    query = """
    MERGE(cluster:GKECluster{id:{ClusterSelfLink}})
    ON CREATE SET
        cluster.firstseen = timestamp(),
        cluster.created_at = {ClusterCreateTime}
    SET
        cluster.name = {ClusterName},
        cluster.self_link = {ClusterSelfLink},
        cluster.description = {ClusterDescription},
        cluster.logging_service = {ClusterLoggingService},
        cluster.monitoring_service = {ClusterMonitoringService},
        cluster.network = {ClusterNetwork},
        cluster.subnetwork = {ClusterSubnetwork},
        cluster.cluster_ipv4cidr = {ClusterIPv4Cidr},
        cluster.zone = {ClusterZone},
        cluster.location = {ClusterLocation},
        cluster.endpoint = {ClusterEndpoint},
        cluster.initial_version = {ClusterInitialVersion},
        cluster.current_master_version = {ClusterMasterVersion},
        cluster.status = {ClusterStatus},
        cluster.services_ipv4cidr = {ClusterServicesIPv4Cidr},
        cluster.database_encryption = {ClusterDatabaseEncryption},
        cluster.network_policy = {ClusterNetworkPolicy},
        cluster.master_authorized_networks = {ClusterMasterAuthorizedNetworks},
        cluster.legacy_abac = {ClusterAbac},
        cluster.shielded_nodes = {ClusterShieldedNodes},
        cluster.private_nodes = {ClusterPrivateNodes},
        cluster.private_endpoint_enabled = {ClusterPrivateEndpointEnabled},
        cluster.private_endpoint = {ClusterPrivateEndpoint},
        cluster.public_endpoint = {ClusterPublicEndpoint},
        cluster.masterauth_username = {ClusterMasterUsername},
        cluster.masterauth_password = {ClusterMasterPassword}
    WITH cluster
    MATCH (owner:GCPProject{id:{ProjectId}})
    MERGE (owner)-[r:RESOURCE]->(cluster)
    ON CREATE SET r.firstseen = timestamp()
    SET r.lastupdated = {gcp_update_tag}
    """
    for cluster in gke_list.get('clusters', []):
        neo4j_session.run(
            query,
            ProjectId=project_id,
            ClusterSelfLink=cluster['selfLink'],
            ClusterCreateTime=cluster['createTime'],
            ClusterName=cluster['name'],
            ClusterDescription=cluster.get('description'),
            ClusterLoggingService=cluster.get('loggingService'),
            ClusterMonitoringService=cluster.get('monitoringService'),
            ClusterNetwork=cluster.get('network'),
            ClusterSubnetwork=cluster.get('subnetwork'),
            ClusterIPv4Cidr=cluster.get('clusterIpv4Cidr'),
            ClusterZone=cluster.get('zone'),
            ClusterLocation=cluster.get('location'),
            ClusterEndpoint=cluster.get('endpoint'),
            ClusterInitialVersion=cluster.get('initialClusterVersion'),
            ClusterMasterVersion=cluster.get('currentMasterVersion'),
            ClusterStatus=cluster.get('status'),
            ClusterServicesIPv4Cidr=cluster.get('servicesIpv4Cidr'),
            ClusterDatabaseEncryption=cluster.get('databaseEncryption', {}).get('state'),
            ClusterNetworkPolicy=_process_network_policy(cluster),
            ClusterMasterAuthorizedNetworks=cluster.get('masterAuthorizedNetworksConfig', {}).get('enabled'),
            ClusterAbac=cluster.get('legacyAbac', {}).get('enabled'),
            ClusterShieldedNodes=cluster.get('shieldedNodes', {}).get('enabled'),
            ClusterPrivateNodes=cluster.get('privateClusterConfig', {}).get('enablePrivateNodes'),
            ClusterPrivateEndpointEnabled=cluster.get('privateClusterConfig', {}).get('enablePrivateEndpoint'),
            ClusterPrivateEndpoint=cluster.get('privateClusterConfig', {}).get('privateEndpoint'),
            ClusterPublicEndpoint=cluster.get('privateClusterConfig', {}).get('publicEndpoint'),
            ClusterMasterUsername=cluster.get('masterAuth', {}).get('username'),
            ClusterMasterPassword=cluster.get('masterAuth', {}).get('password'),
            gcp_update_tag=gcp_update_tag,
        )