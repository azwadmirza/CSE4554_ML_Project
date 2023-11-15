    def search_novel(self, query):
        response = self.submit_form(search_url, {
            'searchword': query
        })
        data = response.json()

        results = []
        for novel in data:
            titleSoup = BeautifulSoup(novel['name'], 'lxml')
            results.append({
                'title': titleSoup.body.text.title(),
                'url': novel_page_url % novel['id_encode'],
                'info': 'Latest: %s' % novel['lastchapter'],
            })
        # end for
        return results