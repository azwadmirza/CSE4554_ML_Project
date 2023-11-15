    def _get_page(self, task, config, url):
        login_response = requests.get(url)
        if login_response.url == url:
            log.debug('Already logged in')
            return login_response
        elif login_response.url != 'https://mijn.npo.nl/inloggen':
            raise plugin.PluginError('Unexpected login page: {}'.format(login_response.url))

        login_page = get_soup(login_response.content)
        token = login_page.find('input', attrs={'name': 'authenticity_token'})['value']

        email = config.get('email')
        password = config.get('password')

        try:
            profile_response = requests.post('https://mijn.npo.nl/sessions',
                                                  {'authenticity_token': token,
                                                   'email': email,
                                                   'password': password})
        except requests.RequestException as e:
            raise plugin.PluginError('Request error: %s' % e.args[0])

        if profile_response.url == 'https://mijn.npo.nl/sessions':
            raise plugin.PluginError('Failed to login. Check username and password.')
        elif profile_response.url != url:
            raise plugin.PluginError('Unexpected page: {} (expected {})'.format(profile_response.url, url))

        return profile_response