def dec_file(name, out=None, **kwargs):
    '''
    This is a helper function to decrypt a file and return its contents.

    You can provide an optional output file using `out`

    `name` can be a local file or when not using `salt-run` can be a url like `salt://`, `https://` etc.

    CLI Examples:

    .. code-block:: bash

        salt-run nacl.dec_file name=/tmp/id_rsa.nacl
        salt-run nacl.dec_file name=/tmp/id_rsa.nacl box_type=secretbox \
            sk_file=/etc/salt/pki/master/nacl.pub
    '''
    try:
        data = __salt__['cp.get_file_str'](name)
    except Exception as e:
        # likly using salt-run so fallback to local filesystem
        with salt.utils.files.fopen(name, 'rb') as f:
            data = f.read()
    d = dec(data, **kwargs)
    if out:
        if os.path.isfile(out):
            raise Exception('file:{0} already exist.'.format(out))
        with salt.utils.files.fopen(out, 'wb') as f:
            f.write(d)
        return 'Wrote: {0}'.format(out)
    return d