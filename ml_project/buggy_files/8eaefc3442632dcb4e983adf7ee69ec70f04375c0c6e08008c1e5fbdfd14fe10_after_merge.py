    def compile_pillar(self):
        '''
        Render the pillar data and return
        '''
        top, terrors = self.get_top()
        matches = self.top_matches(top)
        pillar, errors = self.render_pillar(matches)
        self.ext_pillar(pillar)
        errors.extend(terrors)
        if self.opts.get('pillar_opts', True):
            mopts = dict(self.opts)
            if 'grains' in mopts:
                mopts.pop('grains')
            if 'aes' in mopts:
                mopts.pop('aes')
            # Restore the actual file_roots path. Issue 5449
            mopts['file_roots'] = self.actual_file_roots
            mopts['saltversion'] = __version__
            pillar['master'] = mopts
        if errors:
            for error in errors:
                log.critical('Pillar render error: {0}'.format(error))
            pillar['_errors'] = errors
        return pillar