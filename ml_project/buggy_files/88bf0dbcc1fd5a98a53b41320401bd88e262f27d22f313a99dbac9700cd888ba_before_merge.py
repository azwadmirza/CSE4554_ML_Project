def _create_self_signed_key_vault_certificate(cli_ctx, vault_base_url, certificate_name, certificate_policy, certificate_output_folder=None, disabled=False, tags=None, validity=None):
    CertificateAttributes = get_sdk(cli_ctx, ResourceType.DATA_KEYVAULT, 'models.certificate_attributes#CertificateAttributes')
    cert_attrs = CertificateAttributes(enabled=not disabled)
    logger.info("Starting long-running operation 'keyvault certificate create'")
    if validity is not None:
        certificate_policy['x509_certificate_properties']['validity_in_months'] = validity
    client = _get_keyVault_not_arm_client(cli_ctx)
    client.create_certificate(
        vault_base_url, certificate_name, certificate_policy, cert_attrs, tags)

    # otherwise loop until the certificate creation is complete
    while True:
        check = client.get_certificate_operation(
            vault_base_url, certificate_name)
        if check.status != 'inProgress':
            logger.info("Long-running operation 'keyvault certificate create' finished with result %s.",
                        check)
            break
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Long-running operation wait cancelled.")
            raise
        except Exception as client_exception:
            message = getattr(client_exception, 'message', client_exception)
            import json
            try:
                message = str(message) + ' ' + json.loads(
                    client_exception.response.text)['error']['details'][0]['message']   # pylint: disable=no-member
            except:  # pylint: disable=bare-except
                pass

            raise CLIError('{}'.format(message))

    pem_output_folder = None
    if certificate_output_folder is not None:
        pem_output_folder = os.path.join(
            certificate_output_folder, certificate_name + '.pem')
        pfx_output_folder = os.path.join(
            certificate_output_folder, certificate_name + '.pfx')
        _download_secret(cli_ctx, vault_base_url, certificate_name,
                         pem_output_folder, pfx_output_folder)
    return client.get_certificate(vault_base_url, certificate_name, ''), pem_output_folder