    def process_info(self, info_dict):
        """Process a single resolved IE result."""

        assert info_dict.get('_type', 'video') == 'video'
        #We increment the download the download count here to match the previous behaviour.
        self.increment_downloads()

        info_dict['fulltitle'] = info_dict['title']
        if len(info_dict['title']) > 200:
            info_dict['title'] = info_dict['title'][:197] + u'...'

        # Keep for backwards compatibility
        info_dict['stitle'] = info_dict['title']

        if not 'format' in info_dict:
            info_dict['format'] = info_dict['ext']

        reason = self._match_entry(info_dict)
        if reason is not None:
            self.to_screen(u'[download] ' + reason)
            return

        max_downloads = self.params.get('max_downloads')
        if max_downloads is not None:
            if self._num_downloads > int(max_downloads):
                raise MaxDownloadsReached()

        filename = self.prepare_filename(info_dict)

        # Forced printings
        if self.params.get('forcetitle', False):
            compat_print(info_dict['title'])
        if self.params.get('forceid', False):
            compat_print(info_dict['id'])
        if self.params.get('forceurl', False):
            # For RTMP URLs, also include the playpath
            compat_print(info_dict['url'] + info_dict.get('play_path', u''))
        if self.params.get('forcethumbnail', False) and 'thumbnail' in info_dict:
            compat_print(info_dict['thumbnail'])
        if self.params.get('forcedescription', False) and 'description' in info_dict:
            compat_print(info_dict['description'])
        if self.params.get('forcefilename', False) and filename is not None:
            compat_print(filename)
        if self.params.get('forceformat', False):
            compat_print(info_dict['format'])

        # Do nothing else if in simulate mode
        if self.params.get('simulate', False):
            return

        if filename is None:
            return

        try:
            dn = os.path.dirname(encodeFilename(filename))
            if dn != '' and not os.path.exists(dn):
                os.makedirs(dn)
        except (OSError, IOError) as err:
            self.report_error(u'unable to create directory ' + compat_str(err))
            return

        if self.params.get('writedescription', False):
            try:
                descfn = filename + u'.description'
                self.report_writedescription(descfn)
                with io.open(encodeFilename(descfn), 'w', encoding='utf-8') as descfile:
                    descfile.write(info_dict['description'])
            except (OSError, IOError):
                self.report_error(u'Cannot write description file ' + descfn)
                return

        subtitles_are_requested = any([self.params.get('writesubtitles', False),
                                       self.params.get('writeautomaticsub'),
                                       self.params.get('allsubtitles', False)])

        if  subtitles_are_requested and 'subtitles' in info_dict and info_dict['subtitles']:
            # subtitles download errors are already managed as troubles in relevant IE
            # that way it will silently go on when used with unsupporting IE
            subtitles = info_dict['subtitles']
            sub_format = self.params.get('subtitlesformat')
            for sub_lang in subtitles.keys():
                sub = subtitles[sub_lang]
                if sub is None:
                    continue
                try:
                    sub_filename = subtitles_filename(filename, sub_lang, sub_format)
                    self.report_writesubtitles(sub_filename)
                    with io.open(encodeFilename(sub_filename), 'w', encoding='utf-8') as subfile:
                            subfile.write(sub)
                except (OSError, IOError):
                    self.report_error(u'Cannot write subtitles file ' + descfn)
                    return

        if self.params.get('writeinfojson', False):
            infofn = filename + u'.info.json'
            self.report_writeinfojson(infofn)
            try:
                json_info_dict = dict((k, v) for k,v in info_dict.items() if not k in ['urlhandle'])
                write_json_file(json_info_dict, encodeFilename(infofn))
            except (OSError, IOError):
                self.report_error(u'Cannot write metadata to JSON file ' + infofn)
                return

        if self.params.get('writethumbnail', False):
            if info_dict.get('thumbnail') is not None:
                thumb_format = determine_ext(info_dict['thumbnail'], u'jpg')
                thumb_filename = filename.rpartition('.')[0] + u'.' + thumb_format
                self.to_screen(u'[%s] %s: Downloading thumbnail ...' %
                               (info_dict['extractor'], info_dict['id']))
                uf = compat_urllib_request.urlopen(info_dict['thumbnail'])
                with open(thumb_filename, 'wb') as thumbf:
                    shutil.copyfileobj(uf, thumbf)
                self.to_screen(u'[%s] %s: Writing thumbnail to: %s' %
                               (info_dict['extractor'], info_dict['id'], thumb_filename))

        if not self.params.get('skip_download', False):
            if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(filename)):
                success = True
            else:
                try:
                    success = self.fd._do_download(filename, info_dict)
                except (OSError, IOError) as err:
                    raise UnavailableVideoError(err)
                except (compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error) as err:
                    self.report_error(u'unable to download video data: %s' % str(err))
                    return
                except (ContentTooShortError, ) as err:
                    self.report_error(u'content too short (expected %s bytes and served %s)' % (err.expected, err.downloaded))
                    return

            if success:
                try:
                    self.post_process(filename, info_dict)
                except (PostProcessingError) as err:
                    self.report_error(u'postprocessing: %s' % str(err))
                    return