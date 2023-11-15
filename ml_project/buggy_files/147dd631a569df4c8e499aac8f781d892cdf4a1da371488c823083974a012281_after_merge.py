    def _real_extract(self, url):
        url, smuggled_data = unsmuggle_url(url, {})

        proto = (
            'http' if self._downloader.params.get('prefer_insecure', False)
            else 'https')

        start_time = None
        end_time = None
        parsed_url = compat_urllib_parse_urlparse(url)
        for component in [parsed_url.fragment, parsed_url.query]:
            query = compat_parse_qs(component)
            if start_time is None and 't' in query:
                start_time = parse_duration(query['t'][0])
            if start_time is None and 'start' in query:
                start_time = parse_duration(query['start'][0])
            if end_time is None and 'end' in query:
                end_time = parse_duration(query['end'][0])

        # Extract original video URL from URL with redirection, like age verification, using next_url parameter
        mobj = re.search(self._NEXT_URL_RE, url)
        if mobj:
            url = proto + '://www.youtube.com/' + compat_urllib_parse_unquote(mobj.group(1)).lstrip('/')
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

        dash_mpds = []

        def add_dash_mpd(video_info):
            dash_mpd = video_info.get('dashmpd')
            if dash_mpd and dash_mpd[0] not in dash_mpds:
                dash_mpds.append(dash_mpd[0])

        # Get video info
        embed_webpage = None
        is_live = None
        if re.search(r'player-age-gate-content">', video_webpage) is not None:
            age_gate = True
            # We simulate the access to the video from www.youtube.com/v/{video_id}
            # this can be viewed without login into Youtube
            url = proto + '://www.youtube.com/embed/%s' % video_id
            embed_webpage = self._download_webpage(url, video_id, 'Downloading embed webpage')
            data = compat_urllib_parse.urlencode({
                'video_id': video_id,
                'eurl': 'https://youtube.googleapis.com/v/' + video_id,
                'sts': self._search_regex(
                    r'"sts"\s*:\s*(\d+)', embed_webpage, 'sts', default=''),
            })
            video_info_url = proto + '://www.youtube.com/get_video_info?' + data
            video_info_webpage = self._download_webpage(
                video_info_url, video_id,
                note='Refetching age-gated info webpage',
                errnote='unable to download video info webpage')
            video_info = compat_parse_qs(video_info_webpage)
            add_dash_mpd(video_info)
        else:
            age_gate = False
            video_info = None
            # Try looking directly into the video webpage
            mobj = re.search(r';ytplayer\.config\s*=\s*({.*?});ytplayer', video_webpage)
            if mobj:
                json_code = uppercase_escape(mobj.group(1))
                ytplayer_config = json.loads(json_code)
                args = ytplayer_config['args']
                if args.get('url_encoded_fmt_stream_map'):
                    # Convert to the same format returned by compat_parse_qs
                    video_info = dict((k, [v]) for k, v in args.items())
                    add_dash_mpd(video_info)
                if args.get('livestream') == '1' or args.get('live_playback') == 1:
                    is_live = True
            if not video_info or self._downloader.params.get('youtube_include_dash_manifest', True):
                # We also try looking in get_video_info since it may contain different dashmpd
                # URL that points to a DASH manifest with possibly different itag set (some itags
                # are missing from DASH manifest pointed by webpage's dashmpd, some - from DASH
                # manifest pointed by get_video_info's dashmpd).
                # The general idea is to take a union of itags of both DASH manifests (for example
                # video with such 'manifest behavior' see https://github.com/rg3/youtube-dl/issues/6093)
                self.report_video_info_webpage_download(video_id)
                for el_type in ['&el=info', '&el=embedded', '&el=detailpage', '&el=vevo', '']:
                    video_info_url = (
                        '%s://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en'
                        % (proto, video_id, el_type))
                    video_info_webpage = self._download_webpage(
                        video_info_url,
                        video_id, note=False,
                        errnote='unable to download video info webpage')
                    get_video_info = compat_parse_qs(video_info_webpage)
                    if get_video_info.get('use_cipher_signature') != ['True']:
                        add_dash_mpd(get_video_info)
                    if not video_info:
                        video_info = get_video_info
                    if 'token' in get_video_info:
                        # Different get_video_info requests may report different results, e.g.
                        # some may report video unavailability, but some may serve it without
                        # any complaint (see https://github.com/rg3/youtube-dl/issues/7362,
                        # the original webpage as well as el=info and el=embedded get_video_info
                        # requests report video unavailability due to geo restriction while
                        # el=detailpage succeeds and returns valid data). This is probably
                        # due to YouTube measures against IP ranges of hosting providers.
                        # Working around by preferring the first succeeded video_info containing
                        # the token if no such video_info yet was found.
                        if 'token' not in video_info:
                            video_info = get_video_info
                        break
        if 'token' not in video_info:
            if 'reason' in video_info:
                if 'The uploader has not made this video available in your country.' in video_info['reason']:
                    regions_allowed = self._html_search_meta('regionsAllowed', video_webpage, default=None)
                    if regions_allowed:
                        raise ExtractorError('YouTube said: This video is available in %s only' % (
                            ', '.join(map(ISO3166Utils.short2full, regions_allowed.split(',')))),
                            expected=True)
                raise ExtractorError(
                    'YouTube said: %s' % video_info['reason'][0],
                    expected=True, video_id=video_id)
            else:
                raise ExtractorError(
                    '"token" parameter not in video info for unknown reason',
                    video_id=video_id)

        # title
        if 'title' in video_info:
            video_title = video_info['title'][0]
        else:
            self._downloader.report_warning('Unable to extract video title')
            video_title = '_'

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

        if 'multifeed_metadata_list' in video_info and not smuggled_data.get('force_singlefeed', False):
            if not self._downloader.params.get('noplaylist'):
                entries = []
                feed_ids = []
                multifeed_metadata_list = compat_urllib_parse_unquote_plus(video_info['multifeed_metadata_list'][0])
                for feed in multifeed_metadata_list.split(','):
                    feed_data = compat_parse_qs(feed)
                    entries.append({
                        '_type': 'url_transparent',
                        'ie_key': 'Youtube',
                        'url': smuggle_url(
                            '%s://www.youtube.com/watch?v=%s' % (proto, feed_data['id'][0]),
                            {'force_singlefeed': True}),
                        'title': '%s (%s)' % (video_title, feed_data['title'][0]),
                    })
                    feed_ids.append(feed_data['id'][0])
                self.to_screen(
                    'Downloading multifeed video (%s) - add --no-playlist to just download video %s'
                    % (', '.join(feed_ids), video_id))
                return self.playlist_result(entries, video_id, video_title, video_description)
            self.to_screen('Downloading just video %s because of --no-playlist' % video_id)

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
        video_uploader = compat_urllib_parse_unquote_plus(video_info['author'][0])

        # uploader_id
        video_uploader_id = None
        mobj = re.search(r'<link itemprop="url" href="http://www.youtube.com/(?:user|channel)/([^"]+)">', video_webpage)
        if mobj is not None:
            video_uploader_id = mobj.group(1)
        else:
            self._downloader.report_warning('unable to extract uploader nickname')

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
            video_thumbnail = compat_urllib_parse_unquote_plus(video_info['thumbnail_url'][0])

        # upload date
        upload_date = self._html_search_meta(
            'datePublished', video_webpage, 'upload date', default=None)
        if not upload_date:
            upload_date = self._search_regex(
                [r'(?s)id="eow-date.*?>(.*?)</span>',
                 r'id="watch-uploader-info".*?>.*?(?:Published|Uploaded|Streamed live|Started) on (.+?)</strong>'],
                video_webpage, 'upload date', default=None)
            if upload_date:
                upload_date = ' '.join(re.sub(r'[/,-]', r' ', mobj.group(1)).split())
        upload_date = unified_strdate(upload_date)

        m_cat_container = self._search_regex(
            r'(?s)<h4[^>]*>\s*Category\s*</h4>\s*<ul[^>]*>(.*?)</ul>',
            video_webpage, 'categories', default=None)
        if m_cat_container:
            category = self._html_search_regex(
                r'(?s)<a[^<]+>(.*?)</a>', m_cat_container, 'category',
                default=None)
            video_categories = None if category is None else [category]
        else:
            video_categories = None

        video_tags = [
            unescapeHTML(m.group('content'))
            for m in re.finditer(self._meta_regex('og:video:tag'), video_webpage)]

        def _extract_count(count_name):
            return str_to_int(self._search_regex(
                r'-%s-button[^>]+><span[^>]+class="yt-uix-button-content"[^>]*>([\d,]+)</span>'
                % re.escape(count_name),
                video_webpage, count_name, default=None))

        like_count = _extract_count('like')
        dislike_count = _extract_count('dislike')

        # subtitles
        video_subtitles = self.extract_subtitles(video_id, video_webpage)
        automatic_captions = self.extract_automatic_captions(video_id, video_webpage)

        if 'length_seconds' not in video_info:
            self._downloader.report_warning('unable to extract video duration')
            video_duration = None
        else:
            video_duration = int(compat_urllib_parse_unquote_plus(video_info['length_seconds'][0]))

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
        elif len(video_info.get('url_encoded_fmt_stream_map', [''])[0]) >= 1 or len(video_info.get('adaptive_fmts', [''])[0]) >= 1:
            encoded_url_map = video_info.get('url_encoded_fmt_stream_map', [''])[0] + ',' + video_info.get('adaptive_fmts', [''])[0]
            if 'rtmpe%3Dyes' in encoded_url_map:
                raise ExtractorError('rtmpe downloads are not supported, see https://github.com/rg3/youtube-dl/issues/343 for more information.', expected=True)
            formats = []
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
                    ASSETS_RE = r'"assets":.+?"js":\s*("[^"]+")'

                    jsplayer_url_json = self._search_regex(
                        ASSETS_RE,
                        embed_webpage if age_gate else video_webpage,
                        'JS player URL (1)', default=None)
                    if not jsplayer_url_json and not age_gate:
                        # We need the embed website after all
                        if embed_webpage is None:
                            embed_url = proto + '://www.youtube.com/embed/%s' % video_id
                            embed_webpage = self._download_webpage(
                                embed_url, video_id, 'Downloading embed webpage')
                        jsplayer_url_json = self._search_regex(
                            ASSETS_RE, embed_webpage, 'JS player URL')

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
                                    [r'html5player-([^/]+?)(?:/html5player(?:-new)?)?\.js', r'(?:www|player)-([^/]+)/base\.js'],
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

                # Some itags are not included in DASH manifest thus corresponding formats will
                # lack metadata (see https://github.com/rg3/youtube-dl/pull/5993).
                # Trying to extract metadata from url_encoded_fmt_stream_map entry.
                mobj = re.search(r'^(?P<width>\d+)[xX](?P<height>\d+)$', url_data.get('size', [''])[0])
                width, height = (int(mobj.group('width')), int(mobj.group('height'))) if mobj else (None, None)
                dct = {
                    'format_id': format_id,
                    'url': url,
                    'player_url': player_url,
                    'filesize': int_or_none(url_data.get('clen', [None])[0]),
                    'tbr': float_or_none(url_data.get('bitrate', [None])[0], 1000),
                    'width': width,
                    'height': height,
                    'fps': int_or_none(url_data.get('fps', [None])[0]),
                    'format_note': url_data.get('quality_label', [None])[0] or url_data.get('quality', [None])[0],
                }
                type_ = url_data.get('type', [None])[0]
                if type_:
                    type_split = type_.split(';')
                    kind_ext = type_split[0].split('/')
                    if len(kind_ext) == 2:
                        kind, ext = kind_ext
                        dct['ext'] = ext
                        if kind in ('audio', 'video'):
                            codecs = None
                            for mobj in re.finditer(
                                    r'(?P<key>[a-zA-Z_-]+)=(?P<quote>["\']?)(?P<val>.+?)(?P=quote)(?:;|$)', type_):
                                if mobj.group('key') == 'codecs':
                                    codecs = mobj.group('val')
                                    break
                            if codecs:
                                codecs = codecs.split(',')
                                if len(codecs) == 2:
                                    acodec, vcodec = codecs[0], codecs[1]
                                else:
                                    acodec, vcodec = (codecs[0], 'none') if kind == 'audio' else ('none', codecs[0])
                                dct.update({
                                    'acodec': acodec,
                                    'vcodec': vcodec,
                                })
                if format_id in self._formats:
                    dct.update(self._formats[format_id])
                formats.append(dct)
        elif video_info.get('hlsvp'):
            manifest_url = video_info['hlsvp'][0]
            url_map = self._extract_from_m3u8(manifest_url, video_id)
            formats = _map_to_format_list(url_map)
        else:
            raise ExtractorError('no conn, hlsvp or url_encoded_fmt_stream_map information found in video info')

        # Look for the DASH manifest
        if self._downloader.params.get('youtube_include_dash_manifest', True):
            dash_mpd_fatal = True
            for dash_manifest_url in dash_mpds:
                dash_formats = {}
                try:
                    for df in self._parse_dash_manifest(
                            video_id, dash_manifest_url, player_url, age_gate, dash_mpd_fatal):
                        # Do not overwrite DASH format found in some previous DASH manifest
                        if df['format_id'] not in dash_formats:
                            dash_formats[df['format_id']] = df
                        # Additional DASH manifests may end up in HTTP Error 403 therefore
                        # allow them to fail without bug report message if we already have
                        # some DASH manifest succeeded. This is temporary workaround to reduce
                        # burst of bug reports until we figure out the reason and whether it
                        # can be fixed at all.
                        dash_mpd_fatal = False
                except (ExtractorError, KeyError) as e:
                    self.report_warning(
                        'Skipping DASH manifest: %r' % e, video_id)
                if dash_formats:
                    # Remove the formats we found through non-DASH, they
                    # contain less info and it can be wrong, because we use
                    # fixed values (for example the resolution). See
                    # https://github.com/rg3/youtube-dl/issues/5774 for an
                    # example.
                    formats = [f for f in formats if f['format_id'] not in dash_formats.keys()]
                    formats.extend(dash_formats.values())

        # Check for malformed aspect ratio
        stretched_m = re.search(
            r'<meta\s+property="og:video:tag".*?content="yt:stretch=(?P<w>[0-9]+):(?P<h>[0-9]+)">',
            video_webpage)
        if stretched_m:
            ratio = float(stretched_m.group('w')) / float(stretched_m.group('h'))
            for f in formats:
                if f.get('vcodec') != 'none':
                    f['stretched_ratio'] = ratio

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
            'tags': video_tags,
            'subtitles': video_subtitles,
            'automatic_captions': automatic_captions,
            'duration': video_duration,
            'age_limit': 18 if age_gate else 0,
            'annotations': video_annotations,
            'webpage_url': proto + '://www.youtube.com/watch?v=%s' % video_id,
            'view_count': view_count,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'average_rating': float_or_none(video_info.get('avg_rating', [None])[0]),
            'formats': formats,
            'is_live': is_live,
            'start_time': start_time,
            'end_time': end_time,
        }