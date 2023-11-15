def friendly_error_message():
    try:
        yield
    except SSLError as e:
        raise errors.UserError('SSL error: %s' % e)
    except ConnectionError:
        if call_silently(['which', 'docker']) != 0:
            if is_mac():
                raise errors.DockerNotFoundMac()
            elif is_ubuntu():
                raise errors.DockerNotFoundUbuntu()
            else:
                raise errors.DockerNotFoundGeneric()
        elif call_silently(['which', 'boot2docker']) == 0:
            raise errors.ConnectionErrorDockerMachine()
        else:
            raise errors.ConnectionErrorGeneric(self.get_client().base_url)