    def compile_pillar(self, ext=True, pillar_dirs=None):
        '''
        Render the pillar data and return
        '''
        top, top_errors = self.get_top()
        if ext:
            if self.opts.get('ext_pillar_first', False):
                self.opts['pillar'], errors = self.ext_pillar({}, pillar_dirs)
                matches = self.top_matches(top)
                pillar, errors = self.render_pillar(matches, errors=errors)
                pillar = merge(pillar,
                               self.opts['pillar'],
                               self.merge_strategy,
                               self.opts.get('renderer', 'yaml'),
                               self.opts.get('pillar_merge_lists', False))
            else:
                matches = self.top_matches(top)
                pillar, errors = self.render_pillar(matches)
                pillar, errors = self.ext_pillar(
                    pillar, pillar_dirs, errors=errors)
        else:
            matches = self.top_matches(top)
            pillar, errors = self.render_pillar(matches)
        errors.extend(top_errors)
        if self.opts.get('pillar_opts', False):
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

        if self.pillar_override and isinstance(self.pillar_override, dict):
            pillar = merge(pillar,
                           self.pillar_override,
                           self.merge_strategy,
                           self.opts.get('renderer', 'yaml'),
                           self.opts.get('pillar_merge_lists', False))

        return pillar