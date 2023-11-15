    def _get_link(self,soup):
        """
        Matches something like
        f("MTE2MDIw&title=Yakusoku+no+Neverland");
        """
        sources_regex = r'>\s*?f\("(.*?)"\);'
        sources_url = re.search(sources_regex,str(soup)).group(1)
        sources_json = helpers.get(f'https://vidstreaming.io/ajax.php?id={sources_url}', referer=self.url).json()

        logger.debug('Sources json: {}'.format(str(sources_json)))
        """
        Maps config vidstreaming sources to json results.
        When adding config in the future make sure "vidstream"
        is in the name in order to pass the check above.
        """
        sources_keys = {
            "vidstream":"source",
            "vidstream_bk":"source_bk"
        }

        """
        Elaborate if statements to get sources_json["source"][0]["file"]
        based on order in config.
        """

        servers = Config._read_config()['siteconfig']['vidstream']['servers']
        print(sources_json["source"][0]["file"])
        for i in servers:
            if i in sources_keys:
                if sources_keys[i] in sources_json:
                    if 'file' in sources_json[sources_keys[i]][0]:
                        return {
                            'stream_url': sources_json[sources_keys[i]][0]['file'],
                            'referer': self.url
                        }

        return {'stream_url':''}