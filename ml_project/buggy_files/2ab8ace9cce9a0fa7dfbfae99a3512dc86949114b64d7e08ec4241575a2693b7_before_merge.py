    def compile_pillar(self, ext=True):
        '''
        Render the pillar data and return
        '''
        top, top_errors = self.get_top()
        if ext:
            if self.opts.get('ext_pillar_first', False):
                self.opts['pillar'], errors = self.ext_pillar(self.pillar_override)
                self.rend = salt.loader.render(self.opts, self.functions)
                matches = self.top_matches(top)
                pillar, errors = self.render_pillar(matches, errors=errors)
                pillar = merge(
                    self.opts['pillar'],
                    pillar,
                    self.merge_strategy,
                    self.opts.get('renderer', 'yaml'),
                    self.opts.get('pillar_merge_lists', False))
            else:
                matches = self.top_matches(top)
                pillar, errors = self.render_pillar(matches)
                pillar, errors = self.ext_pillar(pillar, errors=errors)
        else:
            matches = self.top_matches(top)
            pillar, errors = self.render_pillar(matches)
        errors.extend(top_errors)
        if self.opts.get('pillar_opts', False):
            mopts = dict(self.opts)
            if 'grains' in mopts:
                mopts.pop('grains')
            mopts['saltversion'] = __version__
            pillar['master'] = mopts
        if 'pillar' in self.opts and self.opts.get('ssh_merge_pillar', False):
            pillar = merge(
                self.opts['pillar'],
                pillar,
                self.merge_strategy,
                self.opts.get('renderer', 'yaml'),
                self.opts.get('pillar_merge_lists', False))
        if errors:
            for error in errors:
                log.critical('Pillar render error: %s', error)
            pillar['_errors'] = errors

        if self.pillar_override:
            pillar = merge(
                pillar,
                self.pillar_override,
                self.merge_strategy,
                self.opts.get('renderer', 'yaml'),
                self.opts.get('pillar_merge_lists', False))

        decrypt_errors = self.decrypt_pillar(pillar)
        if decrypt_errors:
            pillar.setdefault('_errors', []).extend(decrypt_errors)

        return pillar