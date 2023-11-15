def _set_parameters_for_default_template(cluster_location,
                                         cluster_name,
                                         admin_password,
                                         certificate_thumbprint,
                                         vault_id,
                                         certificate_id,
                                         reliability_level,
                                         admin_name,
                                         cluster_size,
                                         durability_level,
                                         vm_sku,
                                         os_type,
                                         linux):
    parameter_file, _ = _get_template_file_and_parameters_file(linux)
    parameters = get_file_json(parameter_file)['parameters']
    if parameters is None:
        raise CLIError('Invalid parameters file')
    parameters['clusterLocation']['value'] = cluster_location
    parameters['clusterName']['value'] = cluster_name
    parameters['adminUserName']['value'] = admin_name
    parameters['adminPassword']['value'] = admin_password
    parameters['certificateThumbprint']['value'] = certificate_thumbprint
    parameters['sourceVaultvalue']['value'] = vault_id
    parameters['certificateUrlvalue']['value'] = certificate_id
    parameters['reliabilityLevel']['value'] = reliability_level
    parameters['nt0InstanceCount']['value'] = int(cluster_size)
    parameters['durabilityLevel']['value'] = durability_level
    parameters['vmSku']['value'] = vm_sku
    parameters['vmImageSku']['value'] = os_type
    return parameters