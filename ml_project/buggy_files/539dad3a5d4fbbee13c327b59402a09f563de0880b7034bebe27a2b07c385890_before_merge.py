    def accept(self, match, include_rejected=False):
        '''
        Accept the keys matched
        '''
        def _print_accepted(matches, after_match):
            if 'minions' in after_match:
                accepted = sorted(
                    set(after_match['minions']).difference(
                        set(matches.get('minions', []))
                    )
                )
                for key in accepted:
                    print('Key for minion {0} accepted.'.format(key))

        matches = self.key.name_match(match)
        keys = {}
        if 'minions_pre' in matches:
            keys['minions_pre'] = matches['minions_pre']
        if include_rejected and bool(matches.get('minions_rejected')):
            keys['minions_rejected'] = matches['minions_rejected']
        if not keys:
            msg = (
                'The key glob {0!r} does not match any unaccepted {1}keys.'
                .format(match, 'or rejected ' if include_rejected else '')
            )
            print(msg)
            return
        if not self.opts.get('yes', False):
            print('The following keys are going to be accepted:')
            salt.output.display_output(
                    keys,
                    'key',
                    self.opts)
            try:
                veri = raw_input('Proceed? [n/Y] ')
            except KeyboardInterrupt:
                raise SystemExit("\nExiting on CTRL-c")
            if not veri or veri.lower().startswith('y'):
                _print_accepted(
                    matches,
                    self.key.accept(match, include_rejected=include_rejected)
                )
        else:
            print('The following keys are going to be accepted:')
            salt.output.display_output(
                    keys,
                    'key',
                    self.opts)
            _print_accepted(
                matches,
                self.key.accept(match, include_rejected=include_rejected)
            )