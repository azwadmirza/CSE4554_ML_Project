    def _real_extract(self, url):
        url, data = unsmuggle_url(url, {})
        headers = std_headers.copy()
        if 'http_headers' in data:
            headers.update(data['http_headers'])
        if 'Referer' not in headers:
            headers['Referer'] = url

        # Extract ID from URL
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        orig_url = url
        if mobj.group('pro') or mobj.group('player'):
            url = 'https://player.vimeo.com/video/' + video_id
        else:
            url = 'https://vimeo.com/' + video_id

        # Retrieve video webpage to extract further information
        request = sanitized_Request(url, headers=headers)
        try:
            webpage = self._download_webpage(request, video_id)
        except ExtractorError as ee:
            if isinstance(ee.cause, compat_HTTPError) and ee.cause.code == 403:
                errmsg = ee.cause.read()
                if b'Because of its privacy settings, this video cannot be played here' in errmsg:
                    raise ExtractorError(
                        'Cannot download embed-only video without embedding '
                        'URL. Please call youtube-dl with the URL of the page '
                        'that embeds this video.',
                        expected=True)
            raise

        # Now we begin extracting as much information as we can from what we
        # retrieved. First we extract the information common to all extractors,
        # and latter we extract those that are Vimeo specific.
        self.report_extraction(video_id)

        vimeo_config = self._search_regex(
            r'vimeo\.config\s*=\s*(?:({.+?})|_extend\([^,]+,\s+({.+?})\));', webpage,
            'vimeo config', default=None)
        if vimeo_config:
            seed_status = self._parse_json(vimeo_config, video_id).get('seed_status', {})
            if seed_status.get('state') == 'failed':
                raise ExtractorError(
                    '%s said: %s' % (self.IE_NAME, seed_status['title']),
                    expected=True)

        # Extract the config JSON
        try:
            try:
                config_url = self._html_search_regex(
                    r' data-config-url="(.+?)"', webpage,
                    'config URL', default=None)
                if not config_url:
                    # Sometimes new react-based page is served instead of old one that require
                    # different config URL extraction approach (see
                    # https://github.com/rg3/youtube-dl/pull/7209)
                    vimeo_clip_page_config = self._search_regex(
                        r'vimeo\.clip_page_config\s*=\s*({.+?});', webpage,
                        'vimeo clip page config')
                    config_url = self._parse_json(
                        vimeo_clip_page_config, video_id)['player']['config_url']
                config_json = self._download_webpage(config_url, video_id)
                config = json.loads(config_json)
            except RegexNotFoundError:
                # For pro videos or player.vimeo.com urls
                # We try to find out to which variable is assigned the config dic
                m_variable_name = re.search('(\w)\.video\.id', webpage)
                if m_variable_name is not None:
                    config_re = r'%s=({[^}].+?});' % re.escape(m_variable_name.group(1))
                else:
                    config_re = [r' = {config:({.+?}),assets:', r'(?:[abc])=({.+?});']
                config = self._search_regex(config_re, webpage, 'info section',
                                            flags=re.DOTALL)
                config = json.loads(config)
        except Exception as e:
            if re.search('The creator of this video has not given you permission to embed it on this domain.', webpage):
                raise ExtractorError('The author has restricted the access to this video, try with the "--referer" option')

            if re.search(r'<form[^>]+?id="pw_form"', webpage) is not None:
                if '_video_password_verified' in data:
                    raise ExtractorError('video password verification failed!')
                self._verify_video_password(url, video_id, webpage)
                return self._real_extract(
                    smuggle_url(url, {'_video_password_verified': 'verified'}))
            else:
                raise ExtractorError('Unable to extract info section',
                                     cause=e)
        else:
            if config.get('view') == 4:
                config = self._verify_player_video_password(url, video_id)

        if '>You rented this title.<' in webpage:
            feature_id = config.get('video', {}).get('vod', {}).get('feature_id')
            if feature_id and not data.get('force_feature_id', False):
                return self.url_result(smuggle_url(
                    'https://player.vimeo.com/player/%s' % feature_id,
                    {'force_feature_id': True}), 'Vimeo')

        # Extract title
        video_title = config['video']['title']

        # Extract uploader, uploader_url and uploader_id
        video_uploader = config['video'].get('owner', {}).get('name')
        video_uploader_url = config['video'].get('owner', {}).get('url')
        video_uploader_id = video_uploader_url.split('/')[-1] if video_uploader_url else None

        # Extract video thumbnail
        video_thumbnail = config['video'].get('thumbnail')
        if video_thumbnail is None:
            video_thumbs = config['video'].get('thumbs')
            if video_thumbs and isinstance(video_thumbs, dict):
                _, video_thumbnail = sorted((int(width if width.isdigit() else 0), t_url) for (width, t_url) in video_thumbs.items())[-1]

        # Extract video description

        video_description = self._html_search_regex(
            r'(?s)<div\s+class="[^"]*description[^"]*"[^>]*>(.*?)</div>',
            webpage, 'description', default=None)
        if not video_description:
            video_description = self._html_search_meta(
                'description', webpage, default=None)
        if not video_description and mobj.group('pro'):
            orig_webpage = self._download_webpage(
                orig_url, video_id,
                note='Downloading webpage for description',
                fatal=False)
            if orig_webpage:
                video_description = self._html_search_meta(
                    'description', orig_webpage, default=None)
        if not video_description and not mobj.group('player'):
            self._downloader.report_warning('Cannot find video description')

        # Extract video duration
        video_duration = int_or_none(config['video'].get('duration'))

        # Extract upload date
        video_upload_date = None
        mobj = re.search(r'<time[^>]+datetime="([^"]+)"', webpage)
        if mobj is not None:
            video_upload_date = unified_strdate(mobj.group(1))

        try:
            view_count = int(self._search_regex(r'UserPlays:(\d+)', webpage, 'view count'))
            like_count = int(self._search_regex(r'UserLikes:(\d+)', webpage, 'like count'))
            comment_count = int(self._search_regex(r'UserComments:(\d+)', webpage, 'comment count'))
        except RegexNotFoundError:
            # This info is only available in vimeo.com/{id} urls
            view_count = None
            like_count = None
            comment_count = None

        formats = []
        download_request = sanitized_Request('https://vimeo.com/%s?action=load_download_config' % video_id, headers={
            'X-Requested-With': 'XMLHttpRequest'})
        download_data = self._download_json(download_request, video_id, fatal=False)
        if download_data:
            source_file = download_data.get('source_file')
            if isinstance(source_file, dict):
                download_url = source_file.get('download_url')
                if download_url and not source_file.get('is_cold') and not source_file.get('is_defrosting'):
                    source_name = source_file.get('public_name', 'Original')
                    if self._is_valid_url(download_url, video_id, '%s video' % source_name):
                        ext = source_file.get('extension', determine_ext(download_url)).lower()
                        formats.append({
                            'url': download_url,
                            'ext': ext,
                            'width': int_or_none(source_file.get('width')),
                            'height': int_or_none(source_file.get('height')),
                            'filesize': parse_filesize(source_file.get('size')),
                            'format_id': source_name,
                            'preference': 1,
                        })
        config_files = config['video'].get('files') or config['request'].get('files', {})
        for f in config_files.get('progressive', []):
            video_url = f.get('url')
            if not video_url:
                continue
            formats.append({
                'url': video_url,
                'format_id': 'http-%s' % f.get('quality'),
                'width': int_or_none(f.get('width')),
                'height': int_or_none(f.get('height')),
                'fps': int_or_none(f.get('fps')),
                'tbr': int_or_none(f.get('bitrate')),
            })
        m3u8_url = config_files.get('hls', {}).get('url')
        if m3u8_url:
            formats.extend(self._extract_m3u8_formats(
                m3u8_url, video_id, 'mp4', 'm3u8_native', m3u8_id='hls', fatal=False))
        # Bitrates are completely broken. Single m3u8 may contain entries in kbps and bps
        # at the same time without actual units specified. This lead to wrong sorting.
        self._sort_formats(formats, field_preference=('preference', 'height', 'width', 'fps', 'format_id'))

        subtitles = {}
        text_tracks = config['request'].get('text_tracks')
        if text_tracks:
            for tt in text_tracks:
                subtitles[tt['lang']] = [{
                    'ext': 'vtt',
                    'url': 'https://vimeo.com' + tt['url'],
                }]

        return {
            'id': video_id,
            'uploader': video_uploader,
            'uploader_url': video_uploader_url,
            'uploader_id': video_uploader_id,
            'upload_date': video_upload_date,
            'title': video_title,
            'thumbnail': video_thumbnail,
            'description': video_description,
            'duration': video_duration,
            'formats': formats,
            'webpage_url': url,
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'subtitles': subtitles,
        }