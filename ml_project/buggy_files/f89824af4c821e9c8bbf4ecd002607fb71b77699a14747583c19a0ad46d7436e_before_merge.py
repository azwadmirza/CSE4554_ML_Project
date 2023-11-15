    def _get_automatic_captions(self, video_id, webpage):
        """We need the webpage for getting the captions url, pass it as an
           argument to speed up the process."""
        self.to_screen('%s: Looking for automatic captions' % video_id)
        mobj = re.search(r';ytplayer.config = ({.*?});', webpage)
        err_msg = 'Couldn\'t find automatic captions for %s' % video_id
        if mobj is None:
            self._downloader.report_warning(err_msg)
            return {}
        player_config = json.loads(mobj.group(1))
        try:
            args = player_config['args']
            caption_url = args['ttsurl']
            timestamp = args['timestamp']
            # We get the available subtitles
            list_params = compat_urllib_parse.urlencode({
                'type': 'list',
                'tlangs': 1,
                'asrs': 1,
            })
            list_url = caption_url + '&' + list_params
            caption_list = self._download_xml(list_url, video_id)
            original_lang_node = caption_list.find('track')
            if original_lang_node is None:
                self._downloader.report_warning('Video doesn\'t have automatic captions')
                return {}
            original_lang = original_lang_node.attrib['lang_code']
            caption_kind = original_lang_node.attrib.get('kind', '')

            sub_lang_list = {}
            for lang_node in caption_list.findall('target'):
                sub_lang = lang_node.attrib['lang_code']
                sub_formats = []
                for ext in ['sbv', 'vtt', 'srt']:
                    params = compat_urllib_parse.urlencode({
                        'lang': original_lang,
                        'tlang': sub_lang,
                        'fmt': ext,
                        'ts': timestamp,
                        'kind': caption_kind,
                    })
                    sub_formats.append({
                        'url': caption_url + '&' + params,
                        'ext': ext,
                    })
                sub_lang_list[sub_lang] = sub_formats
            return sub_lang_list
        # An extractor error can be raise by the download process if there are
        # no automatic captions but there are subtitles
        except (KeyError, ExtractorError):
            self._downloader.report_warning(err_msg)
            return {}