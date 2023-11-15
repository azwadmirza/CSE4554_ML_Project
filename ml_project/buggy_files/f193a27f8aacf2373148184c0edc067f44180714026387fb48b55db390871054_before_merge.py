    def prepare_filename(self, info_dict):
        """Generate the output filename."""
        try:
            template_dict = dict(info_dict)

            template_dict['epoch'] = int(time.time())
            autonumber_size = self.params.get('autonumber_size')
            if autonumber_size is None:
                autonumber_size = 5
            autonumber_templ = '%0' + str(autonumber_size) + 'd'
            template_dict['autonumber'] = autonumber_templ % self._num_downloads
            if template_dict.get('playlist_index') is not None:
                template_dict['playlist_index'] = '%0*d' % (len(str(template_dict['n_entries'])), template_dict['playlist_index'])
            if template_dict.get('resolution') is None:
                if template_dict.get('width') and template_dict.get('height'):
                    template_dict['resolution'] = '%dx%d' % (template_dict['width'], template_dict['height'])
                elif template_dict.get('height'):
                    template_dict['resolution'] = '%sp' % template_dict['height']
                elif template_dict.get('width'):
                    template_dict['resolution'] = '?x%d' % template_dict['width']

            sanitize = lambda k, v: sanitize_filename(
                compat_str(v),
                restricted=self.params.get('restrictfilenames'),
                is_id=(k == 'id'))
            template_dict = dict((k, sanitize(k, v))
                                 for k, v in template_dict.items()
                                 if v is not None)
            template_dict = collections.defaultdict(lambda: 'NA', template_dict)

            outtmpl = self.params.get('outtmpl', DEFAULT_OUTTMPL)
            tmpl = compat_expanduser(outtmpl)
            filename = tmpl % template_dict
            return filename
        except ValueError as err:
            self.report_error('Error in output template: ' + str(err) + ' (encoding: ' + repr(preferredencoding()) + ')')
            return None