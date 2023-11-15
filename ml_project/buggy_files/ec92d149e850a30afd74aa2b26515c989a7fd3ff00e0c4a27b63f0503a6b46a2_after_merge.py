    def canAddTorrentRssProvider(name, url, cookies, titleTAG):
        """
        See if a Torrent provider can be added
        """
        if not name:
            return json.dumps({'error': 'Invalid name specified'})

        provider_dict = dict(
            zip([x.get_id() for x in sickbeard.torrentRssProviderList], sickbeard.torrentRssProviderList))

        temp_provider = TorrentRssProvider(name, url, cookies, titleTAG)

        if temp_provider.get_id() in provider_dict:
            return json.dumps({'error': 'Exists as {name}'.format(name=provider_dict[temp_provider.get_id()].name)})
        else:
            validate = temp_provider.validate_rss()
            if validate['result']:
                return json.dumps({'success': temp_provider.get_id()})
            else:
                return json.dumps({'error': validate['message']})