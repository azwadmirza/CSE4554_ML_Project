    def _real_extract(self, url):
        proto = (
            'http' if self._downloader.params.get('prefer_insecure', False)
            else 'https')

        # Extract original video URL from URL with redirection, like age verification, using next_url parameter
        mobj = re.search(self._NEXT_URL_RE, url)
        if mobj:
            url = proto + '://www.youtube.com/' + compat_urllib_parse.unquote(mobj.group(1)).lstrip('/')
        video_id = self.extract_id(url)

        # Get video webpage
        url = proto + '://www.youtube.com/watch?v=%s&gl=US&hl=en&has_verified=1&bpctr=9999999999' % video_id
        video_webpage = self._download_webpage(url, video_id)

        # Attempt to extract SWF player URL
        mobj = re.search(r'swfConfig.*?"(https?:\\/\\/.*?watch.*?-.*?\.swf)"', video_webpage)
        if mobj is not None:
            player_url = re.sub(r'\\(.)', r'\1', mobj.group(1))
        else:
            player_url = None

        # Get video info
        if re.search(r'player-age-gate-content">', video_webpage) is not None:
            age_gate = True
            # We simulate the access to the video from www.youtube.com/v/{video_id}
            # this can be viewed without login into Youtube
            data = compat_urllib_parse.urlencode({
                'video_id': video_id,
                'eurl': 'https://youtube.googleapis.com/v/' + video_id,
                'sts': self._search_regex(
                    r'"sts"\s*:\s*(\d+)', video_webpage, 'sts', default=''),
            })
            video_info_url = proto + '://www.youtube.com/get_video_info?' + data
            video_info_webpage = self._download_webpage(
                video_info_url, video_id,
                note='Refetching age-gated info webpage',
                errnote='unable to download video info webpage')
            video_info = compat_parse_qs(video_info_webpage)
        else:
            age_gate = False
            try:
                # Try looking directly into the video webpage
                mobj = re.search(r';ytplayer\.config\s*=\s*({.*?});', video_webpage)
                if not mobj:
                    raise ValueError('Could not find ytplayer.config')  # caught below
                json_code = uppercase_escape(mobj.group(1))
                ytplayer_config = json.loads(json_code)
                args = ytplayer_config['args']
                # Convert to the same format returned by compat_parse_qs
                video_info = dict((k, [v]) for k, v in args.items())
                if 'url_encoded_fmt_stream_map' not in args:
                    raise ValueError('No stream_map present')  # caught below
            except ValueError:
                # We fallback to the get_video_info pages (used by the embed page)
                self.report_video_info_webpage_download(video_id)
                for el_type in ['&el=embedded', '&el=detailpage', '&el=vevo', '']:
                    video_info_url = (
                        '%s://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en'
                        % (proto, video_id, el_type))
                    video_info_webpage = self._download_webpage(
                        video_info_url,
                        video_id, note=False,
                        errnote='unable to download video info webpage')
                    video_info = compat_parse_qs(video_info_webpage)
                    if 'token' in video_info:
                        break
        if 'token' not in video_info:
            if 'reason' in video_info:
                raise ExtractorError(
                    'YouTube said: %s' % video_info['reason'][0],
                    expected=True, video_id=video_id)
            else:
                raise ExtractorError(
                    '"token" parameter not in video info for unknown reason',
                    video_id=video_id)

        if 'view_count' in video_info:
            view_count = int(video_info['view_count'][0])
        else:
            view_count = None

        # Check for "rental" videos
        if 'ypc_video_rental_bar_text' in video_info and 'author' not in video_info:
            raise ExtractorError('"rental" videos not supported')

        # Start extracting information
        self.report_information_extraction(video_id)

        # uploader
        if 'author' not in video_info:
            raise ExtractorError('Unable to extract uploader name')
        video_uploader = compat_urllib_parse.unquote_plus(video_info['author'][0])

        # uploader_id
        video_uploader_id = None
        mobj = re.search(r'<link itemprop="url" href="http://www.youtube.com/(?:user|channel)/([^"]+)">', video_webpage)
        if mobj is not None:
            video_uploader_id = mobj.group(1)
        else:
            self._downloader.report_warning('unable to extract uploader nickname')

        # title
        if 'title' in video_info:
            video_title = video_info['title'][0]
        else:
            self._downloader.report_warning('Unable to extract video title')
            video_title = '_'

        # thumbnail image
        # We try first to get a high quality image:
        m_thumb = re.search(r'<span itemprop="thumbnail".*?href="(.*?)">',
                            video_webpage, re.DOTALL)
        if m_thumb is not None:
            video_thumbnail = m_thumb.group(1)
        elif 'thumbnail_url' not in video_info:
            self._downloader.report_warning('unable to extract video thumbnail')
            video_thumbnail = None
        else:   # don't panic if we can't find it
            video_thumbnail = compat_urllib_parse.unquote_plus(video_info['thumbnail_url'][0])

        # upload date
        upload_date = None
        mobj = re.search(r'(?s)id="eow-date.*?>(.*?)</span>', video_webpage)
        if mobj is None:
            mobj = re.search(
                r'(?s)id="watch-uploader-info".*?>.*?(?:Published|Uploaded|Streamed live) on (.*?)</strong>',
                video_webpage)
        if mobj is not None:
            upload_date = ' '.join(re.sub(r'[/,-]', r' ', mobj.group(1)).split())
            upload_date = unified_strdate(upload_date)

        m_cat_container = self._search_regex(
            r'(?s)<h4[^>]*>\s*Category\s*</h4>\s*<ul[^>]*>(.*?)</ul>',
            video_webpage, 'categories', fatal=False)
        if m_cat_container:
            category = self._html_search_regex(
                r'(?s)<a[^<]+>(.*?)</a>', m_cat_container, 'category',
                default=None)
            video_categories = None if category is None else [category]
        else:
            video_categories = None

        # description
        video_description = get_element_by_id("eow-description", video_webpage)
        if video_description:
            video_description = re.sub(r'''(?x)
                <a\s+
                    (?:[a-zA-Z-]+="[^"]+"\s+)*?
                    title="([^"]+)"\s+
                    (?:[a-zA-Z-]+="[^"]+"\s+)*?
                    class="yt-uix-redirect-link"\s*>
                [^<]+
                </a>
            ''', r'\1', video_description)
            video_description = clean_html(video_description)
        else:
            fd_mobj = re.search(r'<meta name="description" content="([^"]+)"', video_webpage)
            if fd_mobj:
                video_description = unescapeHTML(fd_mobj.group(1))
            else:
                video_description = ''

        def _extract_count(count_name):
            count = self._search_regex(
                r'id="watch-%s"[^>]*>.*?([\d,]+)\s*</span>' % re.escape(count_name),
                video_webpage, count_name, default=None)
            if count is not None:
                return int(count.replace(',', ''))
            return None
        like_count = _extract_count('like')
        dislike_count = _extract_count('dislike')

        # subtitles
        video_subtitles = self.extract_subtitles(video_id, video_webpage)

        if self._downloader.params.get('listsubtitles', False):
            self._list_available_subtitles(video_id, video_webpage)
            return

        if 'length_seconds' not in video_info:
            self._downloader.report_warning('unable to extract video duration')
            video_duration = None
        else:
            video_duration = int(compat_urllib_parse.unquote_plus(video_info['length_seconds'][0]))

        # annotations
        video_annotations = None
        if self._downloader.params.get('writeannotations', False):
            video_annotations = self._extract_annotations(video_id)

        def _map_to_format_list(urlmap):
            formats = []
            for itag, video_real_url in urlmap.items():
                dct = {
                    'format_id': itag,
                    'url': video_real_url,
                    'player_url': player_url,
                }
                if itag in self._formats:
                    dct.update(self._formats[itag])
                formats.append(dct)
            return formats

        if 'conn' in video_info and video_info['conn'][0].startswith('rtmp'):
            self.report_rtmp_download()
            formats = [{
                'format_id': '_rtmp',
                'protocol': 'rtmp',
                'url': video_info['conn'][0],
                'player_url': player_url,
            }]
        elif len(video_info.get('url_encoded_fmt_stream_map', [])) >= 1 or len(video_info.get('adaptive_fmts', [])) >= 1:
            encoded_url_map = video_info.get('url_encoded_fmt_stream_map', [''])[0] + ',' + video_info.get('adaptive_fmts', [''])[0]
            if 'rtmpe%3Dyes' in encoded_url_map:
                raise ExtractorError('rtmpe downloads are not supported, see https://github.com/rg3/youtube-dl/issues/343 for more information.', expected=True)
            url_map = {}
            for url_data_str in encoded_url_map.split(','):
                url_data = compat_parse_qs(url_data_str)
                if 'itag' not in url_data or 'url' not in url_data:
                    continue
                format_id = url_data['itag'][0]
                url = url_data['url'][0]

                if 'sig' in url_data:
                    url += '&signature=' + url_data['sig'][0]
                elif 's' in url_data:
                    encrypted_sig = url_data['s'][0]

                    if not age_gate:
                        jsplayer_url_json = self._search_regex(
                            r'"assets":.+?"js":\s*("[^"]+")',
                            video_webpage, 'JS player URL')
                        player_url = json.loads(jsplayer_url_json)
                    if player_url is None:
                        player_url_json = self._search_regex(
                            r'ytplayer\.config.*?"url"\s*:\s*("[^"]+")',
                            video_webpage, 'age gate player URL')
                        player_url = json.loads(player_url_json)

                    if self._downloader.params.get('verbose'):
                        if player_url is None:
                            player_version = 'unknown'
                            player_desc = 'unknown'
                        else:
                            if player_url.endswith('swf'):
                                player_version = self._search_regex(
                                    r'-(.+?)(?:/watch_as3)?\.swf$', player_url,
                                    'flash player', fatal=False)
                                player_desc = 'flash player %s' % player_version
                            else:
                                player_version = self._search_regex(
                                    r'html5player-([^/]+?)(?:/html5player)?\.js',
                                    player_url,
                                    'html5 player', fatal=False)
                                player_desc = 'html5 player %s' % player_version

                        parts_sizes = self._signature_cache_id(encrypted_sig)
                        self.to_screen('{%s} signature length %s, %s' %
                                       (format_id, parts_sizes, player_desc))

                    signature = self._decrypt_signature(
                        encrypted_sig, video_id, player_url, age_gate)
                    url += '&signature=' + signature
                if 'ratebypass' not in url:
                    url += '&ratebypass=yes'
                url_map[format_id] = url
            formats = _map_to_format_list(url_map)
        elif video_info.get('hlsvp'):
            manifest_url = video_info['hlsvp'][0]
            url_map = self._extract_from_m3u8(manifest_url, video_id)
            formats = _map_to_format_list(url_map)
        else:
            raise ExtractorError('no conn, hlsvp or url_encoded_fmt_stream_map information found in video info')

        # Look for the DASH manifest
        if self._downloader.params.get('youtube_include_dash_manifest', True):
            dash_mpd = video_info.get('dashmpd')
            if not dash_mpd:
                self.report_warning('%s: DASH manifest missing' % video_id)
            else:
                dash_manifest_url = dash_mpd[0]
                try:
                    dash_formats = self._parse_dash_manifest(
                        video_id, dash_manifest_url, player_url, age_gate)
                except (ExtractorError, KeyError) as e:
                    self.report_warning(
                        'Skipping DASH manifest: %r' % e, video_id)
                else:
                    formats.extend(dash_formats)

        self._sort_formats(formats)

        return {
            'id': video_id,
            'uploader': video_uploader,
            'uploader_id': video_uploader_id,
            'upload_date': upload_date,
            'title': video_title,
            'thumbnail': video_thumbnail,
            'description': video_description,
            'categories': video_categories,
            'subtitles': video_subtitles,
            'duration': video_duration,
            'age_limit': 18 if age_gate else 0,
            'annotations': video_annotations,
            'webpage_url': proto + '://www.youtube.com/watch?v=%s' % video_id,
            'view_count': view_count,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'formats': formats,
        }