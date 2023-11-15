    def saveTorrentRssProvider(name, url, cookies, titleTAG):
        """
        Save a Torrent Provider
        """

        if not name or not url:
            return '0'

        provider_dict = dict(zip([x.name for x in sickbeard.torrentRssProviderList], sickbeard.torrentRssProviderList))

        if name in provider_dict:
            provider_dict[name].name = name
            provider_dict[name].url = config.clean_url(url)
            provider_dict[name].cookies = cookies
            provider_dict[name].titleTAG = titleTAG

            return '|'.join([provider_dict[name].get_id(), provider_dict[name].config_string()])

        else:
            new_provider = TorrentRSSProvider(name, url, cookies, titleTAG)
            sickbeard.torrentRssProviderList.append(new_provider)
            return '|'.join([new_provider.get_id(), new_provider.config_string()])