def generate_token(minion_id, signature, impersonated_by_master=False):
    '''
    Generate a Vault token for minion minion_id

    minion_id
        The id of the minion that requests a token

    signature
        Cryptographic signature which validates that the request is indeed sent
        by the minion (or the master, see impersonated_by_master).

    impersonated_by_master
        If the master needs to create a token on behalf of the minion, this is
        True. This happens when the master generates minion pillars.
    '''
    log.debug(
        'Token generation request for %s (impersonated by master: %s)',
        minion_id, impersonated_by_master
    )
    _validate_signature(minion_id, signature, impersonated_by_master)

    try:
        config = __opts__['vault']
        verify = config.get('verify', None)

        if config['auth']['method'] == 'approle':
            if _selftoken_expired():
                log.debug('Vault token expired. Recreating one')
                # Requesting a short ttl token
                url = '{0}/v1/auth/approle/login'.format(config['url'])
                payload = {'role_id': config['auth']['role_id']}
                if 'secret_id' in config['auth']:
                    payload['secret_id'] = config['auth']['secret_id']
                response = requests.post(url, json=payload, verify=verify)
                if response.status_code != 200:
                    return {'error': response.reason}
                config['auth']['token'] = response.json()['auth']['client_token']

        url = '{0}/v1/auth/token/create'.format(config['url'])
        headers = {'X-Vault-Token': config['auth']['token']}
        audit_data = {
            'saltstack-jid': globals().get('__jid__', '<no jid set>'),
            'saltstack-minion': minion_id,
            'saltstack-user': globals().get('__user__', '<no user set>')
        }
        payload = {
                    'policies': _get_policies(minion_id, config),
                    'num_uses': 1,
                    'metadata': audit_data
                  }

        if payload['policies'] == []:
            return {'error': 'No policies matched minion'}

        log.trace('Sending token creation request to Vault')
        response = requests.post(url, headers=headers, json=payload, verify=verify)

        if response.status_code != 200:
            return {'error': response.reason}

        authData = response.json()['auth']
        return {
            'token': authData['client_token'],
            'url': config['url'],
            'verify': verify,
        }
    except Exception as e:
        return {'error': six.text_type(e)}