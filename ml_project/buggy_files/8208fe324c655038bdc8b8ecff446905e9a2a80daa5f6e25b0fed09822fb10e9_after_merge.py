    def reject(self, match, include_accepted=False):
        '''
        Reject the matched keys
        '''
        def _print_rejected(matches, after_match):
            if 'minions_rejected' in after_match:
                rejected = sorted(
                    set(after_match['minions_rejected']).difference(
                        set(matches.get('minions_rejected', []))
                    )
                )
                for key in rejected:
                    print('Key for minion {0} rejected.'.format(key))

        matches = self.key.name_match(match)
        keys = {}
        if 'minions_pre' in matches:
            keys['minions_pre'] = matches['minions_pre']
        if include_accepted and bool(matches.get('minions')):
            keys['minions'] = matches['minions']
        if not keys:
            msg = 'The key glob {0!r} does not match any {1} keys.'.format(
                match,
                'accepted or unaccepted' if include_accepted else 'unaccepted'
            )
            print(msg)
            return
        if not self.opts.get('yes', False):
            print('The following keys are going to be rejected:')
            salt.output.display_output(
                    keys,
                    'key',
                    self.opts)
            veri = raw_input('Proceed? [n/Y] ')
            if veri.lower().startswith('n'):
                return
        _print_rejected(
            matches,
            self.key.reject(
                match_dict=matches,
                include_accepted=include_accepted
            )
        )