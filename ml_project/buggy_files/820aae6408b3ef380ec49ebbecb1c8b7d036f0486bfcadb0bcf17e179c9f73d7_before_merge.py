    def search_novel(self, query):
        query = query.lower().replace(' ', '%20')
        #soup = self.get_soup(search_url % query)

        list_url = search_url % query
        data = self.get_json(list_url)['items'][0]['results']

        results = []
        for item in data:
            url = self.absolute_url("https://www.mtlnovel.com/?p=%s" % item['id'])
            results.append({
                'url': url,
                'title': item['title'],
                'info': self.search_novel_info(url),
            })
        # end for

        return results