    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tr in soup.select('tr'):
            a = tr.select('td a')
            results.append({
                'title': a[0].text.strip(),
                'url': self.absolute_url(a[0]['href']),
                'info': a[1].text.strip(),
            })
        # end for

        return results