    def _real_extract(self, url):
        video_id = self._match_id(url)

        # Get video webpage. We are not actually interested in it for normal
        # cases, but need the cookies in order to be able to download the
        # info webpage
        webpage, handle = self._download_webpage_handle(
            'http://www.nicovideo.jp/watch/' + video_id, video_id)
        if video_id.startswith('so'):
            video_id = self._match_id(handle.geturl())

        video_info = self._download_xml(
            'http://ext.nicovideo.jp/api/getthumbinfo/' + video_id, video_id,
            note='Downloading video info page')

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

        # Start extracting information
        title = xpath_text(video_info, './/title')
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

        extension = xpath_text(video_info, './/movie_type')
        if not extension:
            extension = determine_ext(video_real_url)

        thumbnail = (
            xpath_text(video_info, './/thumbnail_url') or
            self._html_search_meta('image', webpage, 'thumbnail', default=None) or
            video_detail.get('thumbnail'))

        description = xpath_text(video_info, './/description')

        timestamp = parse_iso8601(xpath_text(video_info, './/first_retrieve'))
        if not timestamp:
            match = self._html_search_meta('datePublished', webpage, 'date published', default=None)
            if match:
                timestamp = parse_iso8601(match.replace('+', ':00+'))
        if not timestamp and video_detail.get('postedAt'):
            timestamp = parse_iso8601(
                video_detail['postedAt'].replace('/', '-'),
                delimiter=' ', timezone=datetime.timedelta(hours=9))

        view_count = int_or_none(xpath_text(video_info, './/view_counter'))
        if not view_count:
            match = self._html_search_regex(
                r'>Views: <strong[^>]*>([^<]+)</strong>',
                webpage, 'view count', default=None)
            if match:
                view_count = int_or_none(match.replace(',', ''))
        view_count = view_count or video_detail.get('viewCount')

        comment_count = int_or_none(xpath_text(video_info, './/comment_num'))
        if not comment_count:
            match = self._html_search_regex(
                r'>Comments: <strong[^>]*>([^<]+)</strong>',
                webpage, 'comment count', default=None)
            if match:
                comment_count = int_or_none(match.replace(',', ''))
        comment_count = comment_count or video_detail.get('commentCount')

        duration = (parse_duration(
            xpath_text(video_info, './/length') or
            self._html_search_meta(
                'video:duration', webpage, 'video duration', default=None)) or
            video_detail.get('length'))

        webpage_url = xpath_text(video_info, './/watch_url') or url

        if video_info.find('.//ch_id') is not None:
            uploader_id = video_info.find('.//ch_id').text
            uploader = video_info.find('.//ch_name').text
        elif video_info.find('.//user_id') is not None:
            uploader_id = video_info.find('.//user_id').text
            uploader = video_info.find('.//user_nickname').text
        else:
            uploader_id = uploader = None

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