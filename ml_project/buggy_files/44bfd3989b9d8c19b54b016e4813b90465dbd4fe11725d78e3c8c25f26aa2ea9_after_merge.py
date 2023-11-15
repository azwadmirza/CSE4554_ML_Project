    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_id = urlparse(self.novel_url).path.split('/')[1]
        logger.info("Novel Id: %s", self.novel_id)

        self.novel_title = soup.select_one(
            '.series-details .series-name a').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.series-cover .content')['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # self.novel_author
        # logger.info('Novel author: %s', self.novel_author)

        page_count = 1
        try:
            last_page = soup.select('ul.pagingnation li a')[-1]['title']
            page_count = int(last_page.split(' ')[-1])
        except Exception as _:
            logger.exception('Failed to get page-count: %s', self.novel_url)
        # end try
        logger.info('Total pages: %d', page_count)

        logger.info('Getting chapters...')
        futures_to_check = {
            self.executor.submit(
                self.extract_chapter_list,
                i + 1,
            ): str(i)
            for i in range(page_count)
        }
        temp_chapters = dict()
        for future in futures.as_completed(futures_to_check):
            page = int(futures_to_check[future])
            temp_chapters[page] = future.result()
        # end for

        logger.info('Building sorted chapter list...')
        for page in reversed(sorted(temp_chapters.keys())):
            for chap in reversed(temp_chapters[page]):
                chap['id'] = len(self.chapters) + 1
                chap['volume'] = len(self.chapters) // 100 + 1
                self.chapters.append(chap)
            # end for
        # end for

        self.volumes = [{'id': i + 1}
                        for i in range(1 + len(self.chapters) // 100)]