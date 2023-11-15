    def _get_series_info(self, task, config, series_name, series_url):
        log.info('Retrieving series info for %s', series_name)
        response = requests.get(series_url)
        page = get_soup(response.content)
        tvseries = page.find('div', itemscope='itemscope', itemtype='https://schema.org/TVSeries')
        series_info = Entry()  # create a stub to store the common values for all episodes of this series
        series_info['npo_url'] = tvseries.find('a', itemprop='url')['href']
        series_info['npo_name'] = tvseries.find('span', itemprop='name').contents[0]
        series_info['npo_description'] = tvseries.find('span', itemprop='description').contents[0]
        series_info['npo_language'] = tvseries.find('span', itemprop='inLanguage').contents[0]

        return series_info