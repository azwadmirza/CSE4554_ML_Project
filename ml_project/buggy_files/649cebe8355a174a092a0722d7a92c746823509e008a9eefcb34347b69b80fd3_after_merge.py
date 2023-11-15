def finger_master():
    '''
    Return the fingerprint of the master's public key on the minion.

    CLI Example:

    .. code-block:: bash

        salt '*' key.finger_master
    '''
    return salt.utils.pem_finger(
            os.path.join(__opts__['pki_dir'], 'minion_master.pub'),
	    sum_type=__opts__['hash_type']
            )