def get_password_data(
        name=None,
        kwargs=None,
        instance_id=None,
        call=None,
    ):
    '''
    Return password data for a Windows instance.

    By default only the encrypted password data will be returned. However, if a
    key_file is passed in, then a decrypted password will also be returned.

    Note that the key_file references the private key that was used to generate
    the keypair associated with this instance. This private key will _not_ be
    transmitted to Amazon; it is only used internally inside of Salt Cloud to
    decrypt data _after_ it has been received from Amazon.

    CLI Examples:

    .. code-block:: bash

        salt-cloud -a get_password_data mymachine
        salt-cloud -a get_password_data mymachine key_file=/root/ec2key.pem

    Note: PKCS1_v1_5 was added in PyCrypto 2.5
    '''
    if call != 'action':
        raise SaltCloudSystemExit(
            'The get_password_data action must be called with '
            '-a or --action.'
        )

    if not instance_id:
        instance_id = _get_node(name)['instanceId']

    if kwargs is None:
        kwargs = {}

    if instance_id is None:
        if 'instance_id' in kwargs:
            instance_id = kwargs['instance_id']
            del kwargs['instance_id']

    params = {'Action': 'GetPasswordData',
              'InstanceId': instance_id}

    ret = {}
    data = aws.query(params,
                     return_root=True,
                     location=get_location(),
                     provider=get_provider(),
                     opts=__opts__,
                     sigver='4')

    for item in data:
        ret[next(six.iterkeys(item))] = next(six.itervalues(item))

    if not HAS_M2 and not HAS_PYCRYPTO:
        return ret

    if 'key' not in kwargs:
        if 'key_file' in kwargs:
            with salt.utils.files.fopen(kwargs['key_file'], 'r') as kf_:
                kwargs['key'] = salt.utils.stringutils.to_unicode(kf_.read())

    if 'key' in kwargs:
        pwdata = ret.get('passwordData', None)
        if pwdata is not None:
            rsa_key = kwargs['key']
            pwdata = base64.b64decode(pwdata)
            if HAS_M2:
                key = RSA.load_key_string(rsa_key.encode('ascii'))
                password = key.private_decrypt(pwdata, RSA.pkcs1_padding)
            else:
                dsize = Crypto.Hash.SHA.digest_size
                sentinel = Crypto.Random.new().read(15 + dsize)
                key_obj = Crypto.PublicKey.RSA.importKey(rsa_key)
                key_obj = PKCS1_v1_5.new(key_obj)
                password = key_obj.decrypt(pwdata, sentinel)
            ret['password'] = password

    return ret