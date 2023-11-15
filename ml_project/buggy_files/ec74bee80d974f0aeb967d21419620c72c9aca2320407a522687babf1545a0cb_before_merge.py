    def _real_extract(self, url):
        if url.startswith('//'):
            return {
                '_type': 'url',
                'url': self.http_scheme() + url,
            }

        parsed_url = compat_urlparse.urlparse(url)
        if not parsed_url.scheme:
            default_search = self._downloader.params.get('default_search')
            if default_search is None:
                default_search = 'fixup_error'

            if default_search in ('auto', 'auto_warning', 'fixup_error'):
                if '/' in url:
                    self._downloader.report_warning('The url doesn\'t specify the protocol, trying with http')
                    return self.url_result('http://' + url)
                elif default_search != 'fixup_error':
                    if default_search == 'auto_warning':
                        if re.match(r'^(?:url|URL)$', url):
                            raise ExtractorError(
                                'Invalid URL:  %r . Call youtube-dl like this:  youtube-dl -v "https://www.youtube.com/watch?v=BaW_jenozKc"  ' % url,
                                expected=True)
                        else:
                            self._downloader.report_warning(
                                'Falling back to youtube search for  %s . Set --default-search "auto" to suppress this warning.' % url)
                    return self.url_result('ytsearch:' + url)

            if default_search in ('error', 'fixup_error'):
                raise ExtractorError(
                    '%r is not a valid URL. '
                    'Set --default-search "ytsearch" (or run  youtube-dl "ytsearch:%s" ) to search YouTube'
                    % (url, url), expected=True)
            else:
                if ':' not in default_search:
                    default_search += ':'
                return self.url_result(default_search + url)

        url, smuggled_data = unsmuggle_url(url)
        force_videoid = None
        is_intentional = smuggled_data and smuggled_data.get('to_generic')
        if smuggled_data and 'force_videoid' in smuggled_data:
            force_videoid = smuggled_data['force_videoid']
            video_id = force_videoid
        else:
            video_id = self._generic_id(url)

        self.to_screen('%s: Requesting header' % video_id)

        head_req = HEADRequest(url)
        head_response = self._request_webpage(
            head_req, video_id,
            note=False, errnote='Could not send HEAD request to %s' % url,
            fatal=False)

        if head_response is not False:
            # Check for redirect
            new_url = head_response.geturl()
            if url != new_url:
                self.report_following_redirect(new_url)
                if force_videoid:
                    new_url = smuggle_url(
                        new_url, {'force_videoid': force_videoid})
                return self.url_result(new_url)

        full_response = None
        if head_response is False:
            request = sanitized_Request(url)
            request.add_header('Accept-Encoding', '*')
            full_response = self._request_webpage(request, video_id)
            head_response = full_response

        info_dict = {
            'id': video_id,
            'title': self._generic_title(url),
            'upload_date': unified_strdate(head_response.headers.get('Last-Modified'))
        }

        # Check for direct link to a video
        content_type = head_response.headers.get('Content-Type', '').lower()
        m = re.match(r'^(?P<type>audio|video|application(?=/(?:ogg$|(?:vnd\.apple\.|x-)?mpegurl)))/(?P<format_id>[^;\s]+)', content_type)
        if m:
            format_id = m.group('format_id')
            if format_id.endswith('mpegurl'):
                formats = self._extract_m3u8_formats(url, video_id, 'mp4')
            elif format_id == 'f4m':
                formats = self._extract_f4m_formats(url, video_id)
            else:
                formats = [{
                    'format_id': m.group('format_id'),
                    'url': url,
                    'vcodec': 'none' if m.group('type') == 'audio' else None
                }]
                info_dict['direct'] = True
            self._sort_formats(formats)
            info_dict['formats'] = formats
            return info_dict

        if not self._downloader.params.get('test', False) and not is_intentional:
            force = self._downloader.params.get('force_generic_extractor', False)
            self._downloader.report_warning(
                '%s on generic information extractor.' % ('Forcing' if force else 'Falling back'))

        if not full_response:
            request = sanitized_Request(url)
            # Some webservers may serve compressed content of rather big size (e.g. gzipped flac)
            # making it impossible to download only chunk of the file (yet we need only 512kB to
            # test whether it's HTML or not). According to youtube-dl default Accept-Encoding
            # that will always result in downloading the whole file that is not desirable.
            # Therefore for extraction pass we have to override Accept-Encoding to any in order
            # to accept raw bytes and being able to download only a chunk.
            # It may probably better to solve this by checking Content-Type for application/octet-stream
            # after HEAD request finishes, but not sure if we can rely on this.
            request.add_header('Accept-Encoding', '*')
            full_response = self._request_webpage(request, video_id)

        first_bytes = full_response.read(512)

        # Is it an M3U playlist?
        if first_bytes.startswith(b'#EXTM3U'):
            info_dict['formats'] = self._extract_m3u8_formats(url, video_id, 'mp4')
            self._sort_formats(info_dict['formats'])
            return info_dict

        # Maybe it's a direct link to a video?
        # Be careful not to download the whole thing!
        if not is_html(first_bytes):
            self._downloader.report_warning(
                'URL could be a direct video link, returning it as such.')
            info_dict.update({
                'direct': True,
                'url': url,
            })
            return info_dict

        webpage = self._webpage_read_content(
            full_response, url, video_id, prefix=first_bytes)

        self.report_extraction(video_id)

        # Is it an RSS feed, a SMIL file, an XSPF playlist or a MPD manifest?
        try:
            doc = compat_etree_fromstring(webpage.encode('utf-8'))
            if doc.tag == 'rss':
                return self._extract_rss(url, video_id, doc)
            elif doc.tag == 'SmoothStreamingMedia':
                info_dict['formats'] = self._parse_ism_formats(doc, url)
                self._sort_formats(info_dict['formats'])
                return info_dict
            elif re.match(r'^(?:{[^}]+})?smil$', doc.tag):
                smil = self._parse_smil(doc, url, video_id)
                self._sort_formats(smil['formats'])
                return smil
            elif doc.tag == '{http://xspf.org/ns/0/}playlist':
                return self.playlist_result(self._parse_xspf(doc, video_id), video_id)
            elif re.match(r'(?i)^(?:{[^}]+})?MPD$', doc.tag):
                info_dict['formats'] = self._parse_mpd_formats(
                    doc, video_id,
                    mpd_base_url=full_response.geturl().rpartition('/')[0],
                    mpd_url=url)
                self._sort_formats(info_dict['formats'])
                return info_dict
            elif re.match(r'^{http://ns\.adobe\.com/f4m/[12]\.0}manifest$', doc.tag):
                info_dict['formats'] = self._parse_f4m_formats(doc, url, video_id)
                self._sort_formats(info_dict['formats'])
                return info_dict
        except compat_xml_parse_error:
            pass

        # Is it a Camtasia project?
        camtasia_res = self._extract_camtasia(url, video_id, webpage)
        if camtasia_res is not None:
            return camtasia_res

        # Sometimes embedded video player is hidden behind percent encoding
        # (e.g. https://github.com/rg3/youtube-dl/issues/2448)
        # Unescaping the whole page allows to handle those cases in a generic way
        webpage = compat_urllib_parse_unquote(webpage)

        # it's tempting to parse this further, but you would
        # have to take into account all the variations like
        #   Video Title - Site Name
        #   Site Name | Video Title
        #   Video Title - Tagline | Site Name
        # and so on and so forth; it's just not practical
        video_title = self._og_search_title(
            webpage, default=None) or self._html_search_regex(
            r'(?s)<title>(.*?)</title>', webpage, 'video title',
            default='video')

        # Try to detect age limit automatically
        age_limit = self._rta_search(webpage)
        # And then there are the jokers who advertise that they use RTA,
        # but actually don't.
        AGE_LIMIT_MARKERS = [
            r'Proudly Labeled <a href="http://www.rtalabel.org/" title="Restricted to Adults">RTA</a>',
        ]
        if any(re.search(marker, webpage) for marker in AGE_LIMIT_MARKERS):
            age_limit = 18

        # video uploader is domain name
        video_uploader = self._search_regex(
            r'^(?:https?://)?([^/]*)/.*', url, 'video uploader')

        video_description = self._og_search_description(webpage, default=None)
        video_thumbnail = self._og_search_thumbnail(webpage, default=None)

        # Helper method
        def _playlist_from_matches(matches, getter=None, ie=None):
            urlrs = orderedSet(
                self.url_result(self._proto_relative_url(getter(m) if getter else m), ie)
                for m in matches)
            return self.playlist_result(
                urlrs, playlist_id=video_id, playlist_title=video_title)

        # Look for Brightcove Legacy Studio embeds
        bc_urls = BrightcoveLegacyIE._extract_brightcove_urls(webpage)
        if bc_urls:
            self.to_screen('Brightcove video detected.')
            entries = [{
                '_type': 'url',
                'url': smuggle_url(bc_url, {'Referer': url}),
                'ie_key': 'BrightcoveLegacy'
            } for bc_url in bc_urls]

            return {
                '_type': 'playlist',
                'title': video_title,
                'id': video_id,
                'entries': entries,
            }

        # Look for Brightcove New Studio embeds
        bc_urls = BrightcoveNewIE._extract_urls(webpage)
        if bc_urls:
            return _playlist_from_matches(bc_urls, ie='BrightcoveNew')

        # Look for ThePlatform embeds
        tp_urls = ThePlatformIE._extract_urls(webpage)
        if tp_urls:
            return _playlist_from_matches(tp_urls, ie='ThePlatform')

        # Look for Vessel embeds
        vessel_urls = VesselIE._extract_urls(webpage)
        if vessel_urls:
            return _playlist_from_matches(vessel_urls, ie=VesselIE.ie_key())

        # Look for embedded rtl.nl player
        matches = re.findall(
            r'<iframe[^>]+?src="((?:https?:)?//(?:www\.)?rtl\.nl/system/videoplayer/[^"]+(?:video_)?embed[^"]+)"',
            webpage)
        if matches:
            return _playlist_from_matches(matches, ie='RtlNl')

        vimeo_urls = VimeoIE._extract_urls(url, webpage)
        if vimeo_urls:
            return _playlist_from_matches(vimeo_urls, ie=VimeoIE.ie_key())

        vid_me_embed_url = self._search_regex(
            r'src=[\'"](https?://vid\.me/[^\'"]+)[\'"]',
            webpage, 'vid.me embed', default=None)
        if vid_me_embed_url is not None:
            return self.url_result(vid_me_embed_url, 'Vidme')

        # Look for embedded YouTube player
        matches = re.findall(r'''(?x)
            (?:
                <iframe[^>]+?src=|
                data-video-url=|
                <embed[^>]+?src=|
                embedSWF\(?:\s*|
                new\s+SWFObject\(
            )
            (["\'])
                (?P<url>(?:https?:)?//(?:www\.)?youtube(?:-nocookie)?\.com/
                (?:embed|v|p)/.+?)
            \1''', webpage)
        if matches:
            return _playlist_from_matches(
                matches, lambda m: unescapeHTML(m[1]))

        # Look for lazyYT YouTube embed
        matches = re.findall(
            r'class="lazyYT" data-youtube-id="([^"]+)"', webpage)
        if matches:
            return _playlist_from_matches(matches, lambda m: unescapeHTML(m))

        # Look for Wordpress "YouTube Video Importer" plugin
        matches = re.findall(r'''(?x)<div[^>]+
            class=(?P<q1>[\'"])[^\'"]*\byvii_single_video_player\b[^\'"]*(?P=q1)[^>]+
            data-video_id=(?P<q2>[\'"])([^\'"]+)(?P=q2)''', webpage)
        if matches:
            return _playlist_from_matches(matches, lambda m: m[-1])

        matches = DailymotionIE._extract_urls(webpage)
        if matches:
            return _playlist_from_matches(matches)

        # Look for embedded Dailymotion playlist player (#3822)
        m = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>(?:https?:)?//(?:www\.)?dailymotion\.[a-z]{2,3}/widget/jukebox\?.+?)\1', webpage)
        if m:
            playlists = re.findall(
                r'list\[\]=/playlist/([^/]+)/', unescapeHTML(m.group('url')))
            if playlists:
                return _playlist_from_matches(
                    playlists, lambda p: '//dailymotion.com/playlist/%s' % p)

        # Look for embedded Wistia player
        match = re.search(
            r'<(?:meta[^>]+?content|iframe[^>]+?src)=(["\'])(?P<url>(?:https?:)?//(?:fast\.)?wistia\.net/embed/iframe/.+?)\1', webpage)
        if match:
            embed_url = self._proto_relative_url(
                unescapeHTML(match.group('url')))
            return {
                '_type': 'url_transparent',
                'url': embed_url,
                'ie_key': 'Wistia',
                'uploader': video_uploader,
            }

        match = re.search(r'(?:id=["\']wistia_|data-wistia-?id=["\']|Wistia\.embed\(["\'])(?P<id>[^"\']+)', webpage)
        if match:
            return {
                '_type': 'url_transparent',
                'url': 'wistia:%s' % match.group('id'),
                'ie_key': 'Wistia',
                'uploader': video_uploader,
            }

        match = re.search(
            r'''(?sx)
                <script[^>]+src=(["'])(?:https?:)?//fast\.wistia\.com/assets/external/E-v1\.js\1[^>]*>.*?
                <div[^>]+class=(["']).*?\bwistia_async_(?P<id>[a-z0-9]+)\b.*?\2
            ''', webpage)
        if match:
            return self.url_result(self._proto_relative_url(
                'wistia:%s' % match.group('id')), 'Wistia')

        # Look for SVT player
        svt_url = SVTIE._extract_url(webpage)
        if svt_url:
            return self.url_result(svt_url, 'SVT')

        # Look for embedded condenast player
        matches = re.findall(
            r'<iframe\s+(?:[a-zA-Z-]+="[^"]+"\s+)*?src="(https?://player\.cnevids\.com/embed/[^"]+")',
            webpage)
        if matches:
            return {
                '_type': 'playlist',
                'entries': [{
                    '_type': 'url',
                    'ie_key': 'CondeNast',
                    'url': ma,
                } for ma in matches],
                'title': video_title,
                'id': video_id,
            }

        # Look for Bandcamp pages with custom domain
        mobj = re.search(r'<meta property="og:url"[^>]*?content="(.*?bandcamp\.com.*?)"', webpage)
        if mobj is not None:
            burl = unescapeHTML(mobj.group(1))
            # Don't set the extractor because it can be a track url or an album
            return self.url_result(burl)

        # Look for embedded Vevo player
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>(?:https?:)?//(?:cache\.)?vevo\.com/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for embedded Viddler player
        mobj = re.search(
            r'<(?:iframe[^>]+?src|param[^>]+?value)=(["\'])(?P<url>(?:https?:)?//(?:www\.)?viddler\.com/(?:embed|player)/.+?)\1',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for NYTimes player
        mobj = re.search(
            r'<iframe[^>]+src=(["\'])(?P<url>(?:https?:)?//graphics8\.nytimes\.com/bcvideo/[^/]+/iframe/embed\.html.+?)\1>',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for Libsyn player
        mobj = re.search(
            r'<iframe[^>]+src=(["\'])(?P<url>(?:https?:)?//html5-player\.libsyn\.com/embed/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for Ooyala videos
        mobj = (re.search(r'player\.ooyala\.com/[^"?]+[?#][^"]*?(?:embedCode|ec)=(?P<ec>[^"&]+)', webpage) or
                re.search(r'OO\.Player\.create\([\'"].*?[\'"],\s*[\'"](?P<ec>.{32})[\'"]', webpage) or
                re.search(r'SBN\.VideoLinkset\.ooyala\([\'"](?P<ec>.{32})[\'"]\)', webpage) or
                re.search(r'data-ooyala-video-id\s*=\s*[\'"](?P<ec>.{32})[\'"]', webpage))
        if mobj is not None:
            embed_token = self._search_regex(
                r'embedToken[\'"]?\s*:\s*[\'"]([^\'"]+)',
                webpage, 'ooyala embed token', default=None)
            return OoyalaIE._build_url_result(smuggle_url(
                mobj.group('ec'), {
                    'domain': url,
                    'embed_token': embed_token,
                }))

        # Look for multiple Ooyala embeds on SBN network websites
        mobj = re.search(r'SBN\.VideoLinkset\.entryGroup\((\[.*?\])', webpage)
        if mobj is not None:
            embeds = self._parse_json(mobj.group(1), video_id, fatal=False)
            if embeds:
                return _playlist_from_matches(
                    embeds, getter=lambda v: OoyalaIE._url_for_embed_code(smuggle_url(v['provider_video_id'], {'domain': url})), ie='Ooyala')

        # Look for Aparat videos
        mobj = re.search(r'<iframe .*?src="(http://www\.aparat\.com/video/[^"]+)"', webpage)
        if mobj is not None:
            return self.url_result(mobj.group(1), 'Aparat')

        # Look for MPORA videos
        mobj = re.search(r'<iframe .*?src="(http://mpora\.(?:com|de)/videos/[^"]+)"', webpage)
        if mobj is not None:
            return self.url_result(mobj.group(1), 'Mpora')

        # Look for embedded NovaMov-based player
        mobj = re.search(
            r'''(?x)<(?:pagespeed_)?iframe[^>]+?src=(["\'])
                    (?P<url>http://(?:(?:embed|www)\.)?
                        (?:novamov\.com|
                           nowvideo\.(?:ch|sx|eu|at|ag|co)|
                           videoweed\.(?:es|com)|
                           movshare\.(?:net|sx|ag)|
                           divxstage\.(?:eu|net|ch|co|at|ag))
                        /embed\.php.+?)\1''', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for embedded Facebook player
        facebook_url = FacebookIE._extract_url(webpage)
        if facebook_url is not None:
            return self.url_result(facebook_url, 'Facebook')

        # Look for embedded VK player
        mobj = re.search(r'<iframe[^>]+?src=(["\'])(?P<url>https?://vk\.com/video_ext\.php.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'VK')

        # Look for embedded Odnoklassniki player
        mobj = re.search(r'<iframe[^>]+?src=(["\'])(?P<url>https?://(?:odnoklassniki|ok)\.ru/videoembed/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'Odnoklassniki')

        # Look for embedded ivi player
        mobj = re.search(r'<embed[^>]+?src=(["\'])(?P<url>https?://(?:www\.)?ivi\.ru/video/player.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'Ivi')

        # Look for embedded Huffington Post player
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>https?://embed\.live\.huffingtonpost\.com/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'HuffPost')

        # Look for embed.ly
        mobj = re.search(r'class=["\']embedly-card["\'][^>]href=["\'](?P<url>[^"\']+)', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))
        mobj = re.search(r'class=["\']embedly-embed["\'][^>]src=["\'][^"\']*url=(?P<url>[^&]+)', webpage)
        if mobj is not None:
            return self.url_result(compat_urllib_parse_unquote(mobj.group('url')))

        # Look for funnyordie embed
        matches = re.findall(r'<iframe[^>]+?src="(https?://(?:www\.)?funnyordie\.com/embed/[^"]+)"', webpage)
        if matches:
            return _playlist_from_matches(
                matches, getter=unescapeHTML, ie='FunnyOrDie')

        # Look for BBC iPlayer embed
        matches = re.findall(r'setPlaylist\("(https?://www\.bbc\.co\.uk/iplayer/[^/]+/[\da-z]{8})"\)', webpage)
        if matches:
            return _playlist_from_matches(matches, ie='BBCCoUk')

        # Look for embedded RUTV player
        rutv_url = RUTVIE._extract_url(webpage)
        if rutv_url:
            return self.url_result(rutv_url, 'RUTV')

        # Look for embedded TVC player
        tvc_url = TVCIE._extract_url(webpage)
        if tvc_url:
            return self.url_result(tvc_url, 'TVC')

        # Look for embedded SportBox player
        sportbox_urls = SportBoxEmbedIE._extract_urls(webpage)
        if sportbox_urls:
            return _playlist_from_matches(sportbox_urls, ie='SportBoxEmbed')

        # Look for embedded XHamster player
        xhamster_urls = XHamsterEmbedIE._extract_urls(webpage)
        if xhamster_urls:
            return _playlist_from_matches(xhamster_urls, ie='XHamsterEmbed')

        # Look for embedded TNAFlixNetwork player
        tnaflix_urls = TNAFlixNetworkEmbedIE._extract_urls(webpage)
        if tnaflix_urls:
            return _playlist_from_matches(tnaflix_urls, ie=TNAFlixNetworkEmbedIE.ie_key())

        # Look for embedded PornHub player
        pornhub_urls = PornHubIE._extract_urls(webpage)
        if pornhub_urls:
            return _playlist_from_matches(pornhub_urls, ie=PornHubIE.ie_key())

        # Look for embedded DrTuber player
        drtuber_urls = DrTuberIE._extract_urls(webpage)
        if drtuber_urls:
            return _playlist_from_matches(drtuber_urls, ie=DrTuberIE.ie_key())

        # Look for embedded RedTube player
        redtube_urls = RedTubeIE._extract_urls(webpage)
        if redtube_urls:
            return _playlist_from_matches(redtube_urls, ie=RedTubeIE.ie_key())

        # Look for embedded Tvigle player
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>(?:https?:)?//cloud\.tvigle\.ru/video/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'Tvigle')

        # Look for embedded TED player
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>https?://embed(?:-ssl)?\.ted\.com/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'TED')

        # Look for embedded Ustream videos
        ustream_url = UstreamIE._extract_url(webpage)
        if ustream_url:
            return self.url_result(ustream_url, UstreamIE.ie_key())

        # Look for embedded arte.tv player
        mobj = re.search(
            r'<(?:script|iframe) [^>]*?src="(?P<url>http://www\.arte\.tv/(?:playerv2/embed|arte_vp/index)[^"]+)"',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'ArteTVEmbed')

        # Look for embedded francetv player
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>(?:https?://)?embed\.francetv\.fr/\?ue=.+?)\1',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for embedded smotri.com player
        smotri_url = SmotriIE._extract_url(webpage)
        if smotri_url:
            return self.url_result(smotri_url, 'Smotri')

        # Look for embedded Myvi.ru player
        myvi_url = MyviIE._extract_url(webpage)
        if myvi_url:
            return self.url_result(myvi_url)

        # Look for embedded soundcloud player
        soundcloud_urls = SoundcloudIE._extract_urls(webpage)
        if soundcloud_urls:
            return _playlist_from_matches(soundcloud_urls, getter=unescapeHTML, ie=SoundcloudIE.ie_key())

        # Look for tunein player
        tunein_urls = TuneInBaseIE._extract_urls(webpage)
        if tunein_urls:
            return _playlist_from_matches(tunein_urls)

        # Look for embedded mtvservices player
        mtvservices_url = MTVServicesEmbeddedIE._extract_url(webpage)
        if mtvservices_url:
            return self.url_result(mtvservices_url, ie='MTVServicesEmbedded')

        # Look for embedded yahoo player
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>https?://(?:screen|movies)\.yahoo\.com/.+?\.html\?format=embed)\1',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'Yahoo')

        # Look for embedded sbs.com.au player
        mobj = re.search(
            r'''(?x)
            (?:
                <meta\s+property="og:video"\s+content=|
                <iframe[^>]+?src=
            )
            (["\'])(?P<url>https?://(?:www\.)?sbs\.com\.au/ondemand/video/.+?)\1''',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'SBS')

        # Look for embedded Cinchcast player
        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>https?://player\.cinchcast\.com/.+?)\1',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'Cinchcast')

        mobj = re.search(
            r'<iframe[^>]+?src=(["\'])(?P<url>https?://m(?:lb)?\.mlb\.com/shared/video/embed/embed\.html\?.+?)\1',
            webpage)
        if not mobj:
            mobj = re.search(
                r'data-video-link=["\'](?P<url>http://m.mlb.com/video/[^"\']+)',
                webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'MLB')

        mobj = re.search(
            r'<(?:iframe|script)[^>]+?src=(["\'])(?P<url>%s)\1' % CondeNastIE.EMBED_URL,
            webpage)
        if mobj is not None:
            return self.url_result(self._proto_relative_url(mobj.group('url'), scheme='http:'), 'CondeNast')

        mobj = re.search(
            r'<iframe[^>]+src="(?P<url>https?://(?:new\.)?livestream\.com/[^"]+/player[^"]+)"',
            webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'Livestream')

        # Look for Zapiks embed
        mobj = re.search(
            r'<iframe[^>]+src="(?P<url>https?://(?:www\.)?zapiks\.fr/index\.php\?.+?)"', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'), 'Zapiks')

        # Look for Kaltura embeds
        kaltura_url = KalturaIE._extract_url(webpage)
        if kaltura_url:
            return self.url_result(smuggle_url(kaltura_url, {'source_url': url}), KalturaIE.ie_key())

        # Look for Eagle.Platform embeds
        eagleplatform_url = EaglePlatformIE._extract_url(webpage)
        if eagleplatform_url:
            return self.url_result(eagleplatform_url, EaglePlatformIE.ie_key())

        # Look for ClipYou (uses Eagle.Platform) embeds
        mobj = re.search(
            r'<iframe[^>]+src="https?://(?P<host>media\.clipyou\.ru)/index/player\?.*\brecord_id=(?P<id>\d+).*"', webpage)
        if mobj is not None:
            return self.url_result('eagleplatform:%(host)s:%(id)s' % mobj.groupdict(), 'EaglePlatform')

        # Look for Pladform embeds
        pladform_url = PladformIE._extract_url(webpage)
        if pladform_url:
            return self.url_result(pladform_url)

        # Look for Videomore embeds
        videomore_url = VideomoreIE._extract_url(webpage)
        if videomore_url:
            return self.url_result(videomore_url)

        # Look for Webcaster embeds
        webcaster_url = WebcasterFeedIE._extract_url(self, webpage)
        if webcaster_url:
            return self.url_result(webcaster_url, ie=WebcasterFeedIE.ie_key())

        # Look for Playwire embeds
        mobj = re.search(
            r'<script[^>]+data-config=(["\'])(?P<url>(?:https?:)?//config\.playwire\.com/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for 5min embeds
        mobj = re.search(
            r'<meta[^>]+property="og:video"[^>]+content="https?://embed\.5min\.com/(?P<id>[0-9]+)/?', webpage)
        if mobj is not None:
            return self.url_result('5min:%s' % mobj.group('id'), 'FiveMin')

        # Look for Crooks and Liars embeds
        mobj = re.search(
            r'<(?:iframe[^>]+src|param[^>]+value)=(["\'])(?P<url>(?:https?:)?//embed\.crooksandliars\.com/(?:embed|v)/.+?)\1', webpage)
        if mobj is not None:
            return self.url_result(mobj.group('url'))

        # Look for NBC Sports VPlayer embeds
        nbc_sports_url = NBCSportsVPlayerIE._extract_url(webpage)
        if nbc_sports_url:
            return self.url_result(nbc_sports_url, 'NBCSportsVPlayer')

        # Look for NBC News embeds
        nbc_news_embed_url = re.search(
            r'<iframe[^>]+src=(["\'])(?P<url>(?:https?:)?//www\.nbcnews\.com/widget/video-embed/[^"\']+)\1', webpage)
        if nbc_news_embed_url:
            return self.url_result(nbc_news_embed_url.group('url'), 'NBCNews')

        # Look for Google Drive embeds
        google_drive_url = GoogleDriveIE._extract_url(webpage)
        if google_drive_url:
            return self.url_result(google_drive_url, 'GoogleDrive')

        # Look for UDN embeds
        mobj = re.search(
            r'<iframe[^>]+src="(?P<url>%s)"' % UDNEmbedIE._PROTOCOL_RELATIVE_VALID_URL, webpage)
        if mobj is not None:
            return self.url_result(
                compat_urlparse.urljoin(url, mobj.group('url')), 'UDNEmbed')

        # Look for Senate ISVP iframe
        senate_isvp_url = SenateISVPIE._search_iframe_url(webpage)
        if senate_isvp_url:
            return self.url_result(senate_isvp_url, 'SenateISVP')

        # Look for Dailymotion Cloud videos
        dmcloud_url = DailymotionCloudIE._extract_dmcloud_url(webpage)
        if dmcloud_url:
            return self.url_result(dmcloud_url, 'DailymotionCloud')

        # Look for OnionStudios embeds
        onionstudios_url = OnionStudiosIE._extract_url(webpage)
        if onionstudios_url:
            return self.url_result(onionstudios_url)

        # Look for ViewLift embeds
        viewlift_url = ViewLiftEmbedIE._extract_url(webpage)
        if viewlift_url:
            return self.url_result(viewlift_url)

        # Look for JWPlatform embeds
        jwplatform_url = JWPlatformIE._extract_url(webpage)
        if jwplatform_url:
            return self.url_result(jwplatform_url, 'JWPlatform')

        # Look for Digiteka embeds
        digiteka_url = DigitekaIE._extract_url(webpage)
        if digiteka_url:
            return self.url_result(self._proto_relative_url(digiteka_url), DigitekaIE.ie_key())

        # Look for Arkena embeds
        arkena_url = ArkenaIE._extract_url(webpage)
        if arkena_url:
            return self.url_result(arkena_url, ArkenaIE.ie_key())

        # Look for Piksel embeds
        piksel_url = PikselIE._extract_url(webpage)
        if piksel_url:
            return self.url_result(piksel_url, PikselIE.ie_key())

        # Look for Limelight embeds
        mobj = re.search(r'LimelightPlayer\.doLoad(Media|Channel|ChannelList)\(["\'](?P<id>[a-z0-9]{32})', webpage)
        if mobj:
            lm = {
                'Media': 'media',
                'Channel': 'channel',
                'ChannelList': 'channel_list',
            }
            return self.url_result(smuggle_url('limelight:%s:%s' % (
                lm[mobj.group(1)], mobj.group(2)), {'source_url': url}),
                'Limelight%s' % mobj.group(1), mobj.group(2))

        mobj = re.search(
            r'''(?sx)
                <object[^>]+class=(["\'])LimelightEmbeddedPlayerFlash\1[^>]*>.*?
                    <param[^>]+
                        name=(["\'])flashVars\2[^>]+
                        value=(["\'])(?:(?!\3).)*mediaId=(?P<id>[a-z0-9]{32})
            ''', webpage)
        if mobj:
            return self.url_result(smuggle_url(
                'limelight:media:%s' % mobj.group('id'),
                {'source_url': url}), 'LimelightMedia', mobj.group('id'))

        # Look for AdobeTVVideo embeds
        mobj = re.search(
            r'<iframe[^>]+src=[\'"]((?:https?:)?//video\.tv\.adobe\.com/v/\d+[^"]+)[\'"]',
            webpage)
        if mobj is not None:
            return self.url_result(
                self._proto_relative_url(unescapeHTML(mobj.group(1))),
                'AdobeTVVideo')

        # Look for Vine embeds
        mobj = re.search(
            r'<iframe[^>]+src=[\'"]((?:https?:)?//(?:www\.)?vine\.co/v/[^/]+/embed/(?:simple|postcard))',
            webpage)
        if mobj is not None:
            return self.url_result(
                self._proto_relative_url(unescapeHTML(mobj.group(1))), 'Vine')

        # Look for VODPlatform embeds
        mobj = re.search(
            r'<iframe[^>]+src=(["\'])(?P<url>(?:https?:)?//(?:www\.)?vod-platform\.net/[eE]mbed/.+?)\1',
            webpage)
        if mobj is not None:
            return self.url_result(
                self._proto_relative_url(unescapeHTML(mobj.group('url'))), 'VODPlatform')

        # Look for Mangomolo embeds
        mobj = re.search(
            r'''(?x)<iframe[^>]+src=(["\'])(?P<url>(?:https?:)?//(?:www\.)?admin\.mangomolo\.com/analytics/index\.php/customers/embed/
                (?:
                    video\?.*?\bid=(?P<video_id>\d+)|
                    index\?.*?\bchannelid=(?P<channel_id>(?:[A-Za-z0-9+/=]|%2B|%2F|%3D)+)
                ).+?)\1''', webpage)
        if mobj is not None:
            info = {
                '_type': 'url_transparent',
                'url': self._proto_relative_url(unescapeHTML(mobj.group('url'))),
                'title': video_title,
                'description': video_description,
                'thumbnail': video_thumbnail,
                'uploader': video_uploader,
            }
            video_id = mobj.group('video_id')
            if video_id:
                info.update({
                    'ie_key': 'MangomoloVideo',
                    'id': video_id,
                })
            else:
                info.update({
                    'ie_key': 'MangomoloLive',
                    'id': mobj.group('channel_id'),
                })
            return info

        # Look for Instagram embeds
        instagram_embed_url = InstagramIE._extract_embed_url(webpage)
        if instagram_embed_url is not None:
            return self.url_result(
                self._proto_relative_url(instagram_embed_url), InstagramIE.ie_key())

        # Look for LiveLeak embeds
        liveleak_url = LiveLeakIE._extract_url(webpage)
        if liveleak_url:
            return self.url_result(liveleak_url, 'LiveLeak')

        # Look for 3Q SDN embeds
        threeqsdn_url = ThreeQSDNIE._extract_url(webpage)
        if threeqsdn_url:
            return {
                '_type': 'url_transparent',
                'ie_key': ThreeQSDNIE.ie_key(),
                'url': self._proto_relative_url(threeqsdn_url),
                'title': video_title,
                'description': video_description,
                'thumbnail': video_thumbnail,
                'uploader': video_uploader,
            }

        # Look for VBOX7 embeds
        vbox7_url = Vbox7IE._extract_url(webpage)
        if vbox7_url:
            return self.url_result(vbox7_url, Vbox7IE.ie_key())

        # Look for DBTV embeds
        dbtv_urls = DBTVIE._extract_urls(webpage)
        if dbtv_urls:
            return _playlist_from_matches(dbtv_urls, ie=DBTVIE.ie_key())

        # Look for Videa embeds
        videa_urls = VideaIE._extract_urls(webpage)
        if videa_urls:
            return _playlist_from_matches(videa_urls, ie=VideaIE.ie_key())

        # Look for 20 minuten embeds
        twentymin_urls = TwentyMinutenIE._extract_urls(webpage)
        if twentymin_urls:
            return _playlist_from_matches(
                twentymin_urls, ie=TwentyMinutenIE.ie_key())

        # Look for Openload embeds
        openload_urls = OpenloadIE._extract_urls(webpage)
        if openload_urls:
            return _playlist_from_matches(
                openload_urls, ie=OpenloadIE.ie_key())

        # Look for VideoPress embeds
        videopress_urls = VideoPressIE._extract_urls(webpage)
        if videopress_urls:
            return _playlist_from_matches(
                videopress_urls, ie=VideoPressIE.ie_key())

        # Look for Rutube embeds
        rutube_urls = RutubeIE._extract_urls(webpage)
        if rutube_urls:
            return _playlist_from_matches(
                rutube_urls, ie=RutubeIE.ie_key())

        # Looking for http://schema.org/VideoObject
        json_ld = self._search_json_ld(
            webpage, video_id, default={}, expected_type='VideoObject')
        if json_ld.get('url'):
            info_dict.update({
                'title': video_title or info_dict['title'],
                'description': video_description,
                'thumbnail': video_thumbnail,
                'age_limit': age_limit
            })
            info_dict.update(json_ld)
            return info_dict

        # Look for HTML5 media
        entries = self._parse_html5_media_entries(url, webpage, video_id, m3u8_id='hls')
        if entries:
            for entry in entries:
                entry.update({
                    'id': video_id,
                    'title': video_title,
                })
                self._sort_formats(entry['formats'])
            return self.playlist_result(entries)

        jwplayer_data_str = self._find_jwplayer_data(webpage)
        if jwplayer_data_str:
            try:
                jwplayer_data = self._parse_json(
                    jwplayer_data_str, video_id, transform_source=js_to_json)
                return self._parse_jwplayer_data(jwplayer_data, video_id)
            except ExtractorError:
                pass

        def check_video(vurl):
            if YoutubeIE.suitable(vurl):
                return True
            if RtmpIE.suitable(vurl):
                return True
            vpath = compat_urlparse.urlparse(vurl).path
            vext = determine_ext(vpath)
            return '.' in vpath and vext not in ('swf', 'png', 'jpg', 'srt', 'sbv', 'sub', 'vtt', 'ttml', 'js')

        def filter_video(urls):
            return list(filter(check_video, urls))

        # Start with something easy: JW Player in SWFObject
        found = filter_video(re.findall(r'flashvars: [\'"](?:.*&)?file=(http[^\'"&]*)', webpage))
        if not found:
            # Look for gorilla-vid style embedding
            found = filter_video(re.findall(r'''(?sx)
                (?:
                    jw_plugins|
                    JWPlayerOptions|
                    jwplayer\s*\(\s*["'][^'"]+["']\s*\)\s*\.setup
                )
                .*?
                ['"]?file['"]?\s*:\s*["\'](.*?)["\']''', webpage))
        if not found:
            # Broaden the search a little bit
            found = filter_video(re.findall(r'[^A-Za-z0-9]?(?:file|source)=(http[^\'"&]*)', webpage))
        if not found:
            # Broaden the findall a little bit: JWPlayer JS loader
            found = filter_video(re.findall(
                r'[^A-Za-z0-9]?(?:file|video_url)["\']?:\s*["\'](http(?![^\'"]+\.[0-9]+[\'"])[^\'"]+)["\']', webpage))
        if not found:
            # Flow player
            found = filter_video(re.findall(r'''(?xs)
                flowplayer\("[^"]+",\s*
                    \{[^}]+?\}\s*,
                    \s*\{[^}]+? ["']?clip["']?\s*:\s*\{\s*
                        ["']?url["']?\s*:\s*["']([^"']+)["']
            ''', webpage))
        if not found:
            # Cinerama player
            found = re.findall(
                r"cinerama\.embedPlayer\(\s*\'[^']+\',\s*'([^']+)'", webpage)
        if not found:
            # Try to find twitter cards info
            # twitter:player:stream should be checked before twitter:player since
            # it is expected to contain a raw stream (see
            # https://dev.twitter.com/cards/types/player#On_twitter.com_via_desktop_browser)
            found = filter_video(re.findall(
                r'<meta (?:property|name)="twitter:player:stream" (?:content|value)="(.+?)"', webpage))
        if not found:
            # We look for Open Graph info:
            # We have to match any number spaces between elements, some sites try to align them (eg.: statigr.am)
            m_video_type = re.findall(r'<meta.*?property="og:video:type".*?content="video/(.*?)"', webpage)
            # We only look in og:video if the MIME type is a video, don't try if it's a Flash player:
            if m_video_type is not None:
                found = filter_video(re.findall(r'<meta.*?property="og:video".*?content="(.*?)"', webpage))
        if not found:
            REDIRECT_REGEX = r'[0-9]{,2};\s*(?:URL|url)=\'?([^\'"]+)'
            found = re.search(
                r'(?i)<meta\s+(?=(?:[a-z-]+="[^"]+"\s+)*http-equiv="refresh")'
                r'(?:[a-z-]+="[^"]+"\s+)*?content="%s' % REDIRECT_REGEX,
                webpage)
            if not found:
                # Look also in Refresh HTTP header
                refresh_header = head_response.headers.get('Refresh')
                if refresh_header:
                    # In python 2 response HTTP headers are bytestrings
                    if sys.version_info < (3, 0) and isinstance(refresh_header, str):
                        refresh_header = refresh_header.decode('iso-8859-1')
                    found = re.search(REDIRECT_REGEX, refresh_header)
            if found:
                new_url = compat_urlparse.urljoin(url, unescapeHTML(found.group(1)))
                self.report_following_redirect(new_url)
                return {
                    '_type': 'url',
                    'url': new_url,
                }

        if not found:
            # twitter:player is a https URL to iframe player that may or may not
            # be supported by youtube-dl thus this is checked the very last (see
            # https://dev.twitter.com/cards/types/player#On_twitter.com_via_desktop_browser)
            embed_url = self._html_search_meta('twitter:player', webpage, default=None)
            if embed_url:
                return self.url_result(embed_url)

        if not found:
            raise UnsupportedError(url)

        entries = []
        for video_url in orderedSet(found):
            video_url = unescapeHTML(video_url)
            video_url = video_url.replace('\\/', '/')
            video_url = compat_urlparse.urljoin(url, video_url)
            video_id = compat_urllib_parse_unquote(os.path.basename(video_url))

            # Sometimes, jwplayer extraction will result in a YouTube URL
            if YoutubeIE.suitable(video_url):
                entries.append(self.url_result(video_url, 'Youtube'))
                continue

            # here's a fun little line of code for you:
            video_id = os.path.splitext(video_id)[0]

            entry_info_dict = {
                'id': video_id,
                'uploader': video_uploader,
                'title': video_title,
                'age_limit': age_limit,
            }

            if RtmpIE.suitable(video_url):
                entry_info_dict.update({
                    '_type': 'url_transparent',
                    'ie_key': RtmpIE.ie_key(),
                    'url': video_url,
                })
                entries.append(entry_info_dict)
                continue

            ext = determine_ext(video_url)
            if ext == 'smil':
                entry_info_dict['formats'] = self._extract_smil_formats(video_url, video_id)
            elif ext == 'xspf':
                return self.playlist_result(self._extract_xspf_playlist(video_url, video_id), video_id)
            elif ext == 'm3u8':
                entry_info_dict['formats'] = self._extract_m3u8_formats(video_url, video_id, ext='mp4')
            elif ext == 'mpd':
                entry_info_dict['formats'] = self._extract_mpd_formats(video_url, video_id)
            elif ext == 'f4m':
                entry_info_dict['formats'] = self._extract_f4m_formats(video_url, video_id)
            elif re.search(r'(?i)\.(?:ism|smil)/manifest', video_url) and video_url != url:
                # Just matching .ism/manifest is not enough to be reliably sure
                # whether it's actually an ISM manifest or some other streaming
                # manifest since there are various streaming URL formats
                # possible (see [1]) as well as some other shenanigans like
                # .smil/manifest URLs that actually serve an ISM (see [2]) and
                # so on.
                # Thus the most reasonable way to solve this is to delegate
                # to generic extractor in order to look into the contents of
                # the manifest itself.
                # 1. https://azure.microsoft.com/en-us/documentation/articles/media-services-deliver-content-overview/#streaming-url-formats
                # 2. https://svs.itworkscdn.net/lbcivod/smil:itwfcdn/lbci/170976.smil/Manifest
                entry_info_dict = self.url_result(
                    smuggle_url(video_url, {'to_generic': True}),
                    GenericIE.ie_key())
            else:
                entry_info_dict['url'] = video_url

            if entry_info_dict.get('formats'):
                self._sort_formats(entry_info_dict['formats'])

            entries.append(entry_info_dict)

        if len(entries) == 1:
            return entries[0]
        else:
            for num, e in enumerate(entries, start=1):
                # 'url' results don't have a title
                if e.get('title') is not None:
                    e['title'] = '%s (%d)' % (e['title'], num)
            return {
                '_type': 'playlist',
                'entries': entries,
            }