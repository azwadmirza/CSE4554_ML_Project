    def real_download(self, filename, info_dict):
        man_url = info_dict['url']
        self.to_screen('[%s] Downloading m3u8 manifest' % self.FD_NAME)
        manifest = self.ydl.urlopen(man_url).read()

        s = manifest.decode('utf-8', 'ignore')

        if not self.can_download(s):
            self.report_warning(
                'hlsnative has detected features it does not support, '
                'extraction will be delegated to ffmpeg')
            fd = FFmpegFD(self.ydl, self.params)
            for ph in self._progress_hooks:
                fd.add_progress_hook(ph)
            return fd.real_download(filename, info_dict)

        total_frags = 0
        for line in s.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                total_frags += 1

        ctx = {
            'filename': filename,
            'total_frags': total_frags,
        }

        self._prepare_and_start_frag_download(ctx)

        extra_query = None
        extra_param_to_segment_url = info_dict.get('extra_param_to_segment_url')
        if extra_param_to_segment_url:
            extra_query = compat_urlparse.parse_qs(extra_param_to_segment_url)
        i = 0
        media_sequence = 0
        decrypt_info = {'METHOD': 'NONE'}
        frags_filenames = []
        for line in s.splitlines():
            line = line.strip()
            if line:
                if not line.startswith('#'):
                    frag_url = (
                        line
                        if re.match(r'^https?://', line)
                        else compat_urlparse.urljoin(man_url, line))
                    frag_filename = '%s-Frag%d' % (ctx['tmpfilename'], i)
                    if extra_query:
                        frag_url = update_url_query(frag_url, extra_query)
                    success = ctx['dl'].download(frag_filename, {'url': frag_url})
                    if not success:
                        return False
                    down, frag_sanitized = sanitize_open(frag_filename, 'rb')
                    frag_content = down.read()
                    down.close()
                    if decrypt_info['METHOD'] == 'AES-128':
                        iv = decrypt_info.get('IV') or compat_struct_pack('>8xq', media_sequence)
                        frag_content = AES.new(
                            decrypt_info['KEY'], AES.MODE_CBC, iv).decrypt(frag_content)
                    ctx['dest_stream'].write(frag_content)
                    frags_filenames.append(frag_sanitized)
                    # We only download the first fragment during the test
                    if self.params.get('test', False):
                        break
                    i += 1
                    media_sequence += 1
                elif line.startswith('#EXT-X-KEY'):
                    decrypt_info = parse_m3u8_attributes(line[11:])
                    if decrypt_info['METHOD'] == 'AES-128':
                        if 'IV' in decrypt_info:
                            decrypt_info['IV'] = binascii.unhexlify(decrypt_info['IV'][2:].zfill(32))
                        if not re.match(r'^https?://', decrypt_info['URI']):
                            decrypt_info['URI'] = compat_urlparse.urljoin(
                                man_url, decrypt_info['URI'])
                        if extra_query:
                            decrypt_info['URI'] = update_url_query(decrypt_info['URI'], extra_query)
                        decrypt_info['KEY'] = self.ydl.urlopen(decrypt_info['URI']).read()
                elif line.startswith('#EXT-X-MEDIA-SEQUENCE'):
                    media_sequence = int(line[22:])

        self._finish_frag_download(ctx)

        for frag_file in frags_filenames:
            os.remove(encodeFilename(frag_file))

        return True