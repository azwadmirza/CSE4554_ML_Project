def crl_managed(name,
                signing_private_key,
                signing_cert=None,
                revoked=None,
                days_valid=100,
                days_remaining=30,
                include_expired=False,
                backup=False,):
    '''
    Manage a Certificate Revocation List

    name:
        Path to the certificate

    signing_private_key:
        The private key that will be used to sign this crl. This is
        usually your CA's private key.

    signing_cert:
        The certificate of the authority that will be used to sign this crl.
        This is usually your CA's certificate.

    revoked:
        A list of certificates to revoke. Must include either a serial number or a
        the certificate itself. Can optionally include the revocation date and
        notAfter date from the certificate. See example below for details.

    days_valid:
        The number of days the certificate should be valid for. Default is 100.

    days_remaining:
        The crl should be automatically recreated if there are less than ``days_remaining``
        days until the crl expires. Set to 0 to disable automatic renewal. Default is 30.

    include_expired:
        Include expired certificates in the CRL. Default is ``False``.

    backup:
        When replacing an existing file, backup the old file on the minion. Default is False.

    Example:

    .. code-block:: yaml

        /etc/pki/ca.crl:
          x509.crl_managed:
            - signing_private_key: /etc/pki/myca.key
            - signing_cert: /etc/pki/myca.crt
            - revoked:
              - compromized_Web_key:
                - certificate: /etc/pki/certs/badweb.crt
                - revocation_date: 2015-03-01 00:00:00
                - reason: keyCompromise
              - terminated_vpn_user:
                - serial_number: D6:D2:DC:D8:4D:5C:C0:F4
                - not_after: 2016-01-01 00:00:00
                - revocation_date: 2015-02-25 00:00:00
                - reason: cessationOfOperation
    '''
    ret = {'name': name, 'changes': {}, 'result': False, 'comment': ''}

    if revoked is None:
        revoked = []

    revoked = _revoked_to_list(revoked)

    current_days_remaining = 0
    current_comp = {}

    if os.path.isfile(name):
        try:
            current = __salt__['x509.read_crl'](crl=name)
            current_comp = current.copy()
            current_comp.pop('Last Update')
            current_notafter = current_comp.pop('Next Update')
            current_days_remaining = (
                    datetime.datetime.strptime(current_notafter, '%Y-%m-%d %H:%M:%S') -
                    datetime.datetime.now()).days
            if days_remaining == 0:
                days_remaining = current_days_remaining - 1
        except salt.exceptions.SaltInvocationError:
            current = '{0} is not a valid CRL.'.format(name)
    else:
        current = '{0} does not exist.'.format(name)

    new_crl = __salt__['x509.create_crl'](text=True, signing_private_key=signing_private_key,
            signing_cert=signing_cert, revoked=revoked, days_valid=days_valid, include_expired=include_expired)

    new = __salt__['x509.read_crl'](crl=new_crl)
    new_comp = new.copy()
    new_comp.pop('Last Update')
    new_comp.pop('Next Update')

    if (current_comp == new_comp and
            current_days_remaining > days_remaining and
            __salt__['x509.verify_crl'](name, signing_cert)):

        ret['result'] = True
        ret['comment'] = 'The crl is already in the correct state'
        return ret

    ret['changes'] = {
            'old': current,
            'new': new, }

    if __opts__['test'] is True:
        ret['result'] = None
        ret['comment'] = 'The crl {0} will be updated.'.format(name)
        return ret

    if os.path.isfile(name) and backup:
        bkroot = os.path.join(__opts__['cachedir'], 'file_backup')
        salt.utils.backup_minion(name, bkroot)

    ret['comment'] = __salt__['x509.write_pem'](text=new_crl, path=name, pem_type='X509 CRL')
    ret['result'] = True

    return ret