    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        def process_column_header(td):
            return td.get_text(strip=True).lower()

        items = []

        with BS4Parser(data, 'html5lib') as html:

            # We need to store the post url, to be used with every result later on.
            post_url = html.find('form', {'method': 'post'})['action']

            table = html.find('table', class_='xMenuT')
            rows = table('tr') if table else []
            row_offset = 1
            if not rows or not len(rows) - row_offset:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            headers = rows[0]('th')
            # 0, 1, subject, poster, group, age
            labels = [process_column_header(header) or idx
                      for idx, header in enumerate(headers)]

            # Skip column headers
            rows = rows[row_offset:]
            for row in rows:
                try:
                    col = dict(list(zip(labels, row('td'))))
                    nzb_id_input = col[0 if mode == 'RSS' else 1].find('input')
                    if not nzb_id_input:
                        continue
                    nzb_id = nzb_id_input['name']
                    # Try and get the the article subject from the weird binsearch format
                    title = self.clean_title(col['subject'].text, mode)

                except AttributeError:
                    log.debug('Parsing rows, that may not always have useful info. Skipping to next.')
                    continue
                if not all([title, nzb_id]):
                    continue

                # Obtain the size from the 'description'
                size_field = BinSearchProvider.size_regex.search(col['subject'].text)
                if size_field:
                    size_field = size_field.group(1)
                size = convert_size(size_field, sep='\xa0') or -1
                size = int(size)

                download_url = urljoin(self.url, '{post_url}|nzb_id={nzb_id}'.format(post_url=post_url, nzb_id=nzb_id))

                # For future use
                # detail_url = 'https://www.binsearch.info/?q={0}'.format(title)
                human_time = True
                date = col['age' if mode != 'RSS' else 'date'].get_text(strip=True).replace('-', ' ')
                if mode == 'RSS':
                    human_time = False
                pubdate_raw = date
                pubdate = self.parse_pubdate(pubdate_raw, human_time=human_time)

                item = {
                    'title': title,
                    'link': download_url,
                    'size': size,
                    'pubdate': pubdate,
                }
                if mode != 'RSS':
                    log.debug('Found result: {0}', title)

                items.append(item)

        return items