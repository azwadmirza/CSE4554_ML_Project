    def __init__(self, server_id=None, api_client=None):

        self.server_id = server_id or None
        if not api_client:
            LOG.debug('No api client provided, attempting to use config file')
            jellyfin_client = Jellyfin(server_id).get_client()
            api_client = jellyfin_client.jellyfin
            addon_data = xbmc.translatePath("special://profile/addon_data/plugin.video.jellyfin/data.json")
            try:
                with open(addon_data, 'rb') as infile:
                    data = json.load(infile)

                    server_data = data['Servers'][0]
                    api_client.config.data['auth.server'] = server_data.get('address')
                    api_client.config.data['auth.server-name'] = server_data.get('Name')
                    api_client.config.data['auth.user_id'] = server_data.get('UserId')
                    api_client.config.data['auth.token'] = server_data.get('AccessToken')
            except Exception as e:
                LOG.warning('Addon appears to not be configured yet: {}'.format(e))

        self.api_client = api_client
        self.server = self.api_client.config.data['auth.server']

        self.stack = []