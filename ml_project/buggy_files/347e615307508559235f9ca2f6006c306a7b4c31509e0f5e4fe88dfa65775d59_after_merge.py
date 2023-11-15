    def _real_extract(self, url):
        video_id = self._match_id(url)

        # Get video webpage. We are not actually interested in it for normal
        # cases, but need the cookies in order to be able to download the
        # info webpage
        webpage, handle = self._download_webpage_handle(
            'http://www.nicovideo.jp/watch/' + video_id, video_id)
        if video_id.startswith('so'):
            video_id = self._match_id(handle.geturl())

        api_data = self._parse_json(self._html_search_regex(
            'data-api-data="([^"]+)"', webpage,
            'API data', default='{}'), video_id)
        video_real_url = try_get(
            api_data, lambda x: x['video']['smileInfo']['url'])

        if video_real_url:
            def get_video_info(items):
                return dict_get(api_data['video'], items)
        else:
            # Get flv info
            flv_info_webpage = self._download_webpage(
                'http://flapi.nicovideo.jp/api/getflv/' + video_id + '?as3=1',
                video_id, 'Downloading flv info')

            flv_info = compat_urlparse.parse_qs(flv_info_webpage)
            if 'url' not in flv_info:
                if 'deleted' in flv_info:
                    raise ExtractorError('The video has been deleted.',
                                         expected=True)
                elif 'closed' in flv_info:
                    raise ExtractorError('Niconico videos now require logging in',
                                         expected=True)
                elif 'error' in flv_info:
                    raise ExtractorError('%s reports error: %s' % (
                        self.IE_NAME, flv_info['error'][0]), expected=True)
                else:
                    raise ExtractorError('Unable to find video URL')

            video_real_url = flv_info['url'][0]

            video_info_xml = self._download_xml(
                'http://ext.nicovideo.jp/api/getthumbinfo/' + video_id,
                video_id, note='Downloading video info page')

            def get_video_info(items):
                if not isinstance(items, list):
                    items = [items]
                for item in items:
                    ret = xpath_text(video_info_xml, './/' + item)
                    if ret:
                        return ret

        # Start extracting information
        title = get_video_info('title')
        if not title:
            title = self._og_search_title(webpage, default=None)
        if not title:
            title = self._html_search_regex(
                r'<span[^>]+class="videoHeaderTitle"[^>]*>([^<]+)</span>',
                webpage, 'video title')

        watch_api_data_string = self._html_search_regex(
            r'<div[^>]+id="watchAPIDataContainer"[^>]+>([^<]+)</div>',
            webpage, 'watch api data', default=None)
        watch_api_data = self._parse_json(watch_api_data_string, video_id) if watch_api_data_string else {}
        video_detail = watch_api_data.get('videoDetail', {})

        extension = get_video_info(['movie_type', 'movieType'])
        if not extension:
            extension = determine_ext(video_real_url)

        thumbnail = (
            get_video_info(['thumbnail_url', 'thumbnailURL']) or
            self._html_search_meta('image', webpage, 'thumbnail', default=None) or
            video_detail.get('thumbnail'))

        description = get_video_info('description')

        timestamp = (parse_iso8601(get_video_info('first_retrieve')) or
                     unified_timestamp(get_video_info('postedDateTime')))
        if not timestamp:
            match = self._html_search_meta('datePublished', webpage, 'date published', default=None)
            if match:
                timestamp = parse_iso8601(match.replace('+', ':00+'))
        if not timestamp and video_detail.get('postedAt'):
            timestamp = parse_iso8601(
                video_detail['postedAt'].replace('/', '-'),
                delimiter=' ', timezone=datetime.timedelta(hours=9))

        view_count = int_or_none(get_video_info(['view_counter', 'viewCount']))
        if not view_count:
            match = self._html_search_regex(
                r'>Views: <strong[^>]*>([^<]+)</strong>',
                webpage, 'view count', default=None)
            if match:
                view_count = int_or_none(match.replace(',', ''))
        view_count = view_count or video_detail.get('viewCount')

        comment_count = (int_or_none(get_video_info('comment_num')) or
                         video_detail.get('commentCount') or
                         try_get(api_data, lambda x: x['thread']['commentCount']))
        if not comment_count:
            match = self._html_search_regex(
                r'>Comments: <strong[^>]*>([^<]+)</strong>',
                webpage, 'comment count', default=None)
            if match:
                comment_count = int_or_none(match.replace(',', ''))

        duration = (parse_duration(
            get_video_info('length') or
            self._html_search_meta(
                'video:duration', webpage, 'video duration', default=None)) or
            video_detail.get('length') or
            get_video_info('duration'))

        webpage_url = get_video_info('watch_url') or url

        owner = api_data.get('owner', {})
        uploader_id = get_video_info(['ch_id', 'user_id']) or owner.get('id')
        uploader = get_video_info(['ch_name', 'user_nickname']) or owner.get('nickname')

        return {
            'id': video_id,
            'url': video_real_url,
            'title': title,
            'ext': extension,
            'format_id': 'economy' if video_real_url.endswith('low') else 'normal',
            'thumbnail': thumbnail,
            'description': description,
            'uploader': uploader,
            'timestamp': timestamp,
            'uploader_id': uploader_id,
            'view_count': view_count,
            'comment_count': comment_count,
            'duration': duration,
            'webpage_url': webpage_url,
        }