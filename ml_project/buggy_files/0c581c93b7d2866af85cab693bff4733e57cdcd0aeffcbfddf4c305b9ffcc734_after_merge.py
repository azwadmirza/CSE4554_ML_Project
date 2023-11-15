    def search_novel(self, query):
        url = search_url % quote(query.lower())
        logger.debug('Visiting: %s', url)
        soup = self.get_soup(url)

        results = []
        for li in soup.select('.book-list-info > ul > li'):
            results.append({
                'title': li.select_one('a h4 b').text.strip(),
                'url': self.absolute_url(li.select_one('.book-img a')['href']),
                'info': li.select_one('.update-info').text.strip(),
            })
        # end for
        return results