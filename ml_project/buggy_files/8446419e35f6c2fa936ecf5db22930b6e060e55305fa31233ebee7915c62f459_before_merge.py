def _new_serial(ca_name, CN):
    '''
    Return a serial number in hex using md5sum, based upon the ca_name and
    CN values

    ca_name
        name of the CA
    CN
        common name in the request
    '''
    hashnum = int(
            hashlib.md5(
                '{0}_{1}_{2}'.format(
                    ca_name,
                    CN,
                    int(time.time()))
                ).hexdigest(),
            16
            )
    log.debug('Hashnum: {0}'.format(hashnum))

    # record the hash somewhere
    cachedir = __opts__['cachedir']
    log.debug('cachedir: {0}'.format(cachedir))
    serial_file = '{0}/{1}.serial'.format(cachedir, ca_name)
    with salt.utils.fopen(serial_file, 'a+') as ofile:
        ofile.write(str(hashnum))

    return hashnum