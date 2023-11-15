    def _real_extract(self, url):
        video_id = self._match_id(url)
        url = 'https://openload.co/embed/%s/' % video_id
        headers = {
            'User-Agent': self._USER_AGENT,
        }

        webpage = self._download_webpage(url, video_id, headers=headers)

        if 'File not found' in webpage or 'deleted by the owner' in webpage:
            raise ExtractorError('File not found', expected=True, video_id=video_id)

        phantom = PhantomJSwrapper(self, required_version='2.0')
        webpage, _ = phantom.get(url, html=webpage, video_id=video_id, headers=headers)

        decoded_id = get_element_by_id('streamurl', webpage)

        video_url = 'https://openload.co/stream/%s?mime=true' % decoded_id

        title = self._og_search_title(webpage, default=None) or self._search_regex(
            r'<span[^>]+class=["\']title["\'][^>]*>([^<]+)', webpage,
            'title', default=None) or self._html_search_meta(
            'description', webpage, 'title', fatal=True)

        entries = self._parse_html5_media_entries(url, webpage, video_id)
        entry = entries[0] if entries else {}
        subtitles = entry.get('subtitles')

        info_dict = {
            'id': video_id,
            'title': title,
            'thumbnail': entry.get('thumbnail') or self._og_search_thumbnail(webpage, default=None),
            'url': video_url,
            # Seems all videos have extensions in their titles
            'ext': determine_ext(title, 'mp4'),
            'subtitles': subtitles,
            'http_headers': headers,
        }
        return info_dict