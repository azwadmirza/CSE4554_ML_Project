def _image_wrapper(attr, *args, **kwargs):
    '''
    Wrapper to run a docker-py function and return a list of dictionaries
    '''
    catch_api_errors = kwargs.pop('catch_api_errors', True)

    if kwargs.pop('client_auth', False):
        # Get credential from the home directory of the user running
        # salt-minion, default auth file for docker (~/.docker/config.json)
        registry_auth_config = {}
        try:
            home = os.path.expanduser("~")
            docker_auth_file = os.path.join(home, '.docker', 'config.json')
            with salt.utils.fopen(docker_auth_file) as fp:
                try:
                    docker_auth = json.load(fp)
                    fp.close()
                except (OSError, IOError) as exc:
                    if exc.errno != errno.ENOENT:
                        log.error('Failed to read docker auth file %s: %s', docker_auth_file, exc)
                        docker_auth = {}
                if isinstance(docker_auth, dict):
                    if 'auths' in docker_auth and isinstance(docker_auth['auths'], dict):
                        for key, data in six.iteritems(docker_auth['auths']):
                            if isinstance(data, dict):
                                email = str(data.get('email', ''))
                                b64_auth = base64.b64decode(data.get('auth', ''))
                                username, password = b64_auth.split(':')
                                registry = 'https://{registry}'.format(registry=key)
                                registry_auth_config.update({registry: {
                                    'username': username,
                                    'password': password,
                                    'email': email
                                }})
        except Exception as e:
            log.debug('dockerng was unable to load credential from ~/.docker/config.json'
                      ' trying with pillar now ({0})'.format(e))
        # Set credentials from pillar - Overwrite auth from config.json
        registry_auth_config.update(__pillar__.get('docker-registries', {}))
        for key, data in six.iteritems(__pillar__):
            if key.endswith('-docker-registries'):
                registry_auth_config.update(data)

        err = (
            '{0} Docker credentials{1}. Please see the dockerng remote '
            'execution module documentation for information on how to '
            'configure authentication.'
        )
        try:
            for registry, creds in six.iteritems(registry_auth_config):
                __context__['docker.client'].login(
                    creds['username'],
                    password=creds['password'],
                    email=creds.get('email'),
                    registry=registry,
                    reauth=creds.get('reauth', False))
        except KeyError:
            raise SaltInvocationError(
                err.format('Incomplete', ' for registry {0}'.format(registry))
            )
        client_timeout = kwargs.pop('client_timeout', None)
        if client_timeout is not None:
            __context__['docker.client'].timeout = client_timeout

    func = getattr(__context__['docker.client'], attr)
    if func is None:
        raise SaltInvocationError('Invalid client action \'{0}\''.format(attr))
    ret = []
    try:
        output = func(*args, **kwargs)
        if not kwargs.get('stream', False):
            output = output.splitlines()
        for line in output:
            ret.append(json.loads(line))
    except docker.errors.APIError as exc:
        if catch_api_errors:
            # Generic handling of Docker API errors
            raise CommandExecutionError(
                'Error {0}: {1}'.format(exc.response.status_code,
                                        exc.explanation)
            )
        else:
            # Allow API errors to be caught further up the stack
            raise
    except Exception as exc:
        raise CommandExecutionError(
            'Error occurred performing docker {0}: {1}'.format(attr, exc)
        )

    return ret