    def _get_link(self,soup):

        # Gets:
        # <input type="hidden" id="id" value="MTEyMzg1">
        # <input type="hidden" id="title" value="Yakusoku+no+Neverland">
        # <input type="hidden" id="typesub" value="SUB">
        # Used to create a download url.
        soup_id = soup.select('input#id')[0]['value']
        soup_title = soup.select('input#title')[0]['value']
        soup_typesub = soup.select('input#typesub')[0].get('value','SUB')

        sources_json = helpers.get(f'https://vidstreaming.io/ajax.php', params = {
            'id':soup_id,
            'typesub':soup_typesub,
            'title':soup_title,
            }, referer=self.url).json()

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

        for i in servers:
            if i in sources_keys:
                if sources_keys[i] in sources_json:
                    if 'file' in sources_json[sources_keys[i]][0]:
                        return {
                            'stream_url': sources_json[sources_keys[i]][0]['file'],
                            'referer': self.url
                        }

        return {'stream_url':''}