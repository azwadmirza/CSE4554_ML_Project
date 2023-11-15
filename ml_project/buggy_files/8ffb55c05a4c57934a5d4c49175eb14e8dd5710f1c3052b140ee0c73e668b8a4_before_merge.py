def _set_parameters_for_customize_template(cmd,
                                           cli_ctx,
                                           resource_group_name,
                                           certificate_file,
                                           certificate_password,
                                           vault_name,
                                           vault_resource_group_name,
                                           certificate_output_folder,
                                           certificate_subject_name,
                                           secret_identifier,
                                           parameter_file):
    cli_ctx = cli_ctx
    parameters = get_file_json(parameter_file)['parameters']
    if parameters is None:
        raise CLIError('Invalid parameters file')
    if SOURCE_VAULT_VALUE in parameters and CERTIFICATE_THUMBPRINT in parameters and CERTIFICATE_URL_VALUE in parameters:
        logger.info('Found primary certificate parameters in parameters file')
        result = _create_certificate(cmd,
                                     cli_ctx,
                                     resource_group_name,
                                     certificate_file,
                                     certificate_password,
                                     vault_name,
                                     vault_resource_group_name,
                                     certificate_output_folder,
                                     certificate_subject_name,
                                     secret_identifier)
        parameters[SOURCE_VAULT_VALUE]['value'] = result[0]
        parameters[CERTIFICATE_URL_VALUE]['value'] = result[1]
        parameters[CERTIFICATE_THUMBPRINT]['value'] = result[2]
        output_file = result[3]
    else:
        if SOURCE_VAULT_VALUE not in parameters and CERTIFICATE_THUMBPRINT not in parameters and CERTIFICATE_URL_VALUE not in parameters:
            logger.info(
                'Primary certificate parameters are not present in parameters file')
        else:
            raise CLIError('The primary certificate parameters names in the parameters file should be specified with' + '\'sourceVaultValue\',\'certificateThumbprint\',\'certificateUrlValue\',' +
                           'if the secondary certificate parameters are specified in the parameters file, the parameters names should be specified with' + '\'secSourceVaultValue\',\'secCertificateThumbprint\',\'secCertificateUrlValue\'')

    if SEC_SOURCE_VAULT_VALUE in parameters and SEC_CERTIFICATE_THUMBPRINT in parameters and SEC_CERTIFICATE_URL_VALUE in parameters:
        logger.info('Found secondary certificate parameters in parameters file')
        result = _create_certificate(cmd,
                                     cli_ctx,
                                     resource_group_name,
                                     certificate_file,
                                     certificate_password,
                                     vault_name,
                                     vault_resource_group_name,
                                     certificate_output_folder,
                                     certificate_subject_name,
                                     secret_identifier)
        parameters[SOURCE_VAULT_VALUE]['value'] = result[0]
        parameters[CERTIFICATE_URL_VALUE]['value'] = result[1]
        parameters[CERTIFICATE_THUMBPRINT]['value'] = result[2]
    else:
        if SEC_SOURCE_VAULT_VALUE not in parameters and SEC_CERTIFICATE_THUMBPRINT not in parameters and SEC_CERTIFICATE_URL_VALUE not in parameters:
            logger.info(
                'Secondary certificate parameters are not present in parameters file')
        else:
            raise CLIError('The primary certificate parameters names in the parameters file should be specified with' + '\'sourceVaultValue\',\'certificateThumbprint\',\'certificateUrlValue\',' +
                           'if the secondary certificate parameters are specified in the parameters file, the parameters names should be specified with' + '\'secSourceVaultValue\',\'secCertificateThumbprint\',\'secCertificateUrlValue\'')
    return parameters, output_file