def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            path=dict(type='path', required=True),
            provider=dict(type='str', choices=['selfsigned', 'assertonly', 'acme']),
            force=dict(type='bool', default=False,),
            csr_path=dict(type='path'),

            # General properties of a certificate
            privatekey_path=dict(type='path'),
            privatekey_passphrase=dict(type='str', no_log=True),
            signature_algorithms=dict(type='list'),
            subject=dict(type='dict'),
            subject_strict=dict(type='bool', default=False),
            issuer=dict(type='dict'),
            issuer_strict=dict(type='bool', default=False),
            has_expired=dict(type='bool', default=False),
            version=dict(type='int'),
            keyUsage=dict(type='list', aliases=['key_usage']),
            keyUsage_strict=dict(type='bool', default=False, aliases=['key_usage_strict']),
            extendedKeyUsage=dict(type='list', aliases=['extended_key_usage'], ),
            extendedKeyUsage_strict=dict(type='bool', default=False, aliases=['extended_key_usage_strict']),
            subjectAltName=dict(type='list', aliases=['subject_alt_name']),
            subjectAltName_strict=dict(type='bool', default=False, aliases=['subject_alt_name_strict']),
            notBefore=dict(type='str', aliases=['not_before']),
            notAfter=dict(type='str', aliases=['not_after']),
            valid_at=dict(type='str'),
            invalid_at=dict(type='str'),
            valid_in=dict(type='int'),

            # provider: selfsigned
            selfsigned_version=dict(type='int', default='3'),
            selfsigned_digest=dict(type='str', default='sha256'),
            selfsigned_notBefore=dict(type='str', aliases=['selfsigned_not_before']),
            selfsigned_notAfter=dict(type='str', aliases=['selfsigned_not_after']),

            # provider: acme
            acme_accountkey_path=dict(type='path'),
            acme_challenge_path=dict(type='path'),
            acme_chain=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
        add_file_common_args=True,
    )

    if not pyopenssl_found:
        module.fail_json(msg='The python pyOpenSSL library is required')
    if module.params['provider'] in ['selfsigned', 'assertonly']:
        try:
            getattr(crypto.X509Req, 'get_extensions')
        except AttributeError:
            module.fail_json(msg='You need to have PyOpenSSL>=0.15')

    base_dir = os.path.dirname(module.params['path'])
    if not os.path.isdir(base_dir):
        module.fail_json(
            name=base_dir,
            msg='The directory %s does not exist or the file is not a directory' % base_dir
        )

    provider = module.params['provider']

    if provider == 'selfsigned':
        certificate = SelfSignedCertificate(module)
    elif provider == 'acme':
        certificate = AcmeCertificate(module)
    else:
        certificate = AssertOnlyCertificate(module)

    if module.params['state'] == 'present':

        if module.check_mode:
            result = certificate.dump(check_mode=True)
            result['changed'] = module.params['force'] or not certificate.check(module)
            module.exit_json(**result)

        try:
            certificate.generate(module)
        except CertificateError as exc:
            module.fail_json(msg=to_native(exc))
    else:

        if module.check_mode:
            result = certificate.dump(check_mode=True)
            result['changed'] = os.path.exists(module.params['path'])
            module.exit_json(**result)

        try:
            certificate.remove()
        except CertificateError as exc:
            module.fail_json(msg=to_native(exc))

    result = certificate.dump()

    module.exit_json(**result)