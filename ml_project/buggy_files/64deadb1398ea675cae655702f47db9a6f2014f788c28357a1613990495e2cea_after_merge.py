    def _download(self, data):
        """ Download all data, even if paginated. """
        page = 1
        results = []

        while True:
            data['page'] = page
            fd = urllib.request.urlopen(self.url+urllib.parse.urlencode(data))
            try:
                result = codecs.decode(fd.read(), encoding='utf-8', errors='replace')
                result = json.loads(result)
            except Exception as e:
                raise IOError("Failed to load return from the HEKClient.") from e
            finally:
                fd.close()
            results.extend(result['result'])

            if not result['overmax']:
                if len(results) > 0:
                    return HEKTable(dict_keys_same(results))
                else:
                    return HEKTable()

            page += 1