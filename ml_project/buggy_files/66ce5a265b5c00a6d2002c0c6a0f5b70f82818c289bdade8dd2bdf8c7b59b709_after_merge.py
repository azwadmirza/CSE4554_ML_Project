    def process_info(self, info_dict):
        """Process a single resolved IE result."""

        assert info_dict.get('_type', 'video') == 'video'

        max_downloads = self.params.get('max_downloads')
        if max_downloads is not None:
            if self._num_downloads >= int(max_downloads):
                raise MaxDownloadsReached()

        info_dict['fulltitle'] = info_dict['title']
        if len(info_dict['title']) > 200:
            info_dict['title'] = info_dict['title'][:197] + '...'

        # Keep for backwards compatibility
        info_dict['stitle'] = info_dict['title']

        if 'format' not in info_dict:
            info_dict['format'] = info_dict['ext']

        reason = self._match_entry(info_dict)
        if reason is not None:
            self.to_screen('[download] ' + reason)
            return

        self._num_downloads += 1

        filename = self.prepare_filename(info_dict)

        # Forced printings
        if self.params.get('forcetitle', False):
            self.to_stdout(info_dict['fulltitle'])
        if self.params.get('forceid', False):
            self.to_stdout(info_dict['id'])
        if self.params.get('forceurl', False):
            if info_dict.get('requested_formats') is not None:
                for f in info_dict['requested_formats']:
                    self.to_stdout(f['url'] + f.get('play_path', ''))
            else:
                # For RTMP URLs, also include the playpath
                self.to_stdout(info_dict['url'] + info_dict.get('play_path', ''))
        if self.params.get('forcethumbnail', False) and info_dict.get('thumbnail') is not None:
            self.to_stdout(info_dict['thumbnail'])
        if self.params.get('forcedescription', False) and info_dict.get('description') is not None:
            self.to_stdout(info_dict['description'])
        if self.params.get('forcefilename', False) and filename is not None:
            self.to_stdout(filename)
        if self.params.get('forceduration', False) and info_dict.get('duration') is not None:
            self.to_stdout(formatSeconds(info_dict['duration']))
        if self.params.get('forceformat', False):
            self.to_stdout(info_dict['format'])
        if self.params.get('forcejson', False):
            info_dict['_filename'] = filename
            self.to_stdout(json.dumps(info_dict))
        if self.params.get('dump_single_json', False):
            info_dict['_filename'] = filename

        # Do nothing else if in simulate mode
        if self.params.get('simulate', False):
            return

        if filename is None:
            return

        try:
            dn = os.path.dirname(encodeFilename(filename))
            if dn and not os.path.exists(dn):
                os.makedirs(dn)
        except (OSError, IOError) as err:
            self.report_error('unable to create directory ' + compat_str(err))
            return

        if self.params.get('writedescription', False):
            descfn = filename + '.description'
            if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(descfn)):
                self.to_screen('[info] Video description is already present')
            else:
                try:
                    self.to_screen('[info] Writing video description to: ' + descfn)
                    with io.open(encodeFilename(descfn), 'w', encoding='utf-8') as descfile:
                        descfile.write(info_dict['description'])
                except (KeyError, TypeError):
                    self.report_warning('There\'s no description to write.')
                except (OSError, IOError):
                    self.report_error('Cannot write description file ' + descfn)
                    return

        if self.params.get('writeannotations', False):
            annofn = filename + '.annotations.xml'
            if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(annofn)):
                self.to_screen('[info] Video annotations are already present')
            else:
                try:
                    self.to_screen('[info] Writing video annotations to: ' + annofn)
                    with io.open(encodeFilename(annofn), 'w', encoding='utf-8') as annofile:
                        annofile.write(info_dict['annotations'])
                except (KeyError, TypeError):
                    self.report_warning('There are no annotations to write.')
                except (OSError, IOError):
                    self.report_error('Cannot write annotations file: ' + annofn)
                    return

        subtitles_are_requested = any([self.params.get('writesubtitles', False),
                                       self.params.get('writeautomaticsub')])

        if subtitles_are_requested and 'subtitles' in info_dict and info_dict['subtitles']:
            # subtitles download errors are already managed as troubles in relevant IE
            # that way it will silently go on when used with unsupporting IE
            subtitles = info_dict['subtitles']
            sub_format = self.params.get('subtitlesformat', 'srt')
            for sub_lang in subtitles.keys():
                sub = subtitles[sub_lang]
                if sub is None:
                    continue
                try:
                    sub_filename = subtitles_filename(filename, sub_lang, sub_format)
                    if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(sub_filename)):
                        self.to_screen('[info] Video subtitle %s.%s is already_present' % (sub_lang, sub_format))
                    else:
                        self.to_screen('[info] Writing video subtitles to: ' + sub_filename)
                        with io.open(encodeFilename(sub_filename), 'w', encoding='utf-8') as subfile:
                            subfile.write(sub)
                except (OSError, IOError):
                    self.report_error('Cannot write subtitles file ' + sub_filename)
                    return

        if self.params.get('writeinfojson', False):
            infofn = os.path.splitext(filename)[0] + '.info.json'
            if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(infofn)):
                self.to_screen('[info] Video description metadata is already present')
            else:
                self.to_screen('[info] Writing video description metadata as JSON to: ' + infofn)
                try:
                    write_json_file(info_dict, infofn)
                except (OSError, IOError):
                    self.report_error('Cannot write metadata to JSON file ' + infofn)
                    return

        if self.params.get('writethumbnail', False):
            if info_dict.get('thumbnail') is not None:
                thumb_format = determine_ext(info_dict['thumbnail'], 'jpg')
                thumb_filename = os.path.splitext(filename)[0] + '.' + thumb_format
                if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(thumb_filename)):
                    self.to_screen('[%s] %s: Thumbnail is already present' %
                                   (info_dict['extractor'], info_dict['id']))
                else:
                    self.to_screen('[%s] %s: Downloading thumbnail ...' %
                                   (info_dict['extractor'], info_dict['id']))
                    try:
                        uf = self.urlopen(info_dict['thumbnail'])
                        with open(thumb_filename, 'wb') as thumbf:
                            shutil.copyfileobj(uf, thumbf)
                        self.to_screen('[%s] %s: Writing thumbnail to: %s' %
                                       (info_dict['extractor'], info_dict['id'], thumb_filename))
                    except (compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error) as err:
                        self.report_warning('Unable to download thumbnail "%s": %s' %
                                            (info_dict['thumbnail'], compat_str(err)))

        if not self.params.get('skip_download', False):
            if self.params.get('nooverwrites', False) and os.path.exists(encodeFilename(filename)):
                success = True
            else:
                try:
                    def dl(name, info):
                        fd = get_suitable_downloader(info)(self, self.params)
                        for ph in self._progress_hooks:
                            fd.add_progress_hook(ph)
                        if self.params.get('verbose'):
                            self.to_stdout('[debug] Invoking downloader on %r' % info.get('url'))
                        return fd.download(name, info)
                    if info_dict.get('requested_formats') is not None:
                        downloaded = []
                        success = True
                        merger = FFmpegMergerPP(self, not self.params.get('keepvideo'))
                        if not merger._executable:
                            postprocessors = []
                            self.report_warning('You have requested multiple '
                                                'formats but ffmpeg or avconv are not installed.'
                                                ' The formats won\'t be merged')
                        else:
                            postprocessors = [merger]
                        for f in info_dict['requested_formats']:
                            new_info = dict(info_dict)
                            new_info.update(f)
                            fname = self.prepare_filename(new_info)
                            fname = prepend_extension(fname, 'f%s' % f['format_id'])
                            downloaded.append(fname)
                            partial_success = dl(fname, new_info)
                            success = success and partial_success
                        info_dict['__postprocessors'] = postprocessors
                        info_dict['__files_to_merge'] = downloaded
                    else:
                        # Just a single file
                        success = dl(filename, info_dict)
                except (compat_urllib_error.URLError, compat_http_client.HTTPException, socket.error) as err:
                    self.report_error('unable to download video data: %s' % str(err))
                    return
                except (OSError, IOError) as err:
                    raise UnavailableVideoError(err)
                except (ContentTooShortError, ) as err:
                    self.report_error('content too short (expected %s bytes and served %s)' % (err.expected, err.downloaded))
                    return

            if success:
                try:
                    self.post_process(filename, info_dict)
                except (PostProcessingError) as err:
                    self.report_error('postprocessing: %s' % str(err))
                    return

        self.record_download_archive(info_dict)