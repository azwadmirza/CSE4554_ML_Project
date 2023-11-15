    def compile_pillar(self, ext=True, pillar_dirs=None):
        '''
        Render the pillar data and return
        '''
        top, top_errors = self.get_top()
        if ext:
            if self.opts.get('ext_pillar_first', False):
                self.opts['pillar'] = self.ext_pillar({}, pillar_dirs)
                matches = self.top_matches(top)
                pillar, errors = self.render_pillar(matches)
                pillar = merge(pillar,
                               self.opts['pillar'],
                               self.merge_strategy,
                               self.opts.get('renderer', 'yaml'))
            else:
                matches = self.top_matches(top)
                pillar, errors = self.render_pillar(matches)
                pillar = self.ext_pillar(pillar, pillar_dirs)
        else:
            matches = self.top_matches(top)
            pillar, errors = self.render_pillar(matches)
        errors.extend(top_errors)
        if self.opts.get('pillar_opts', True):
            mopts = dict(self.opts)
            if 'grains' in mopts:
                mopts.pop('grains')
            # Restore the actual file_roots path. Issue 5449
            mopts['file_roots'] = self.actual_file_roots
            mopts['saltversion'] = __version__
            pillar['master'] = mopts
        if errors:
            for error in errors:
                log.critical('Pillar render error: {0}'.format(error))
            pillar['_errors'] = errors
        return pillar