    def delete(self, match):
        '''
        Delete the matched keys
        '''
        def _print_deleted(matches, after_match):
            deleted = []
            for keydir in ('minions', 'minions_pre', 'minions_rejected'):
                deleted.extend(list(
                    set(matches.get(keydir, [])).difference(
                        set(after_match.get(keydir, []))
                    )
                ))
            for key in sorted(deleted):
                print('Key for minion {0} deleted.'.format(key))

        matches = self.key.name_match(match)
        if not matches:
            print(
                'The key glob {0!r} does not match any accepted, unaccepted '
                'or rejected keys.'.format(match)
            )
            return
        if not self.opts.get('yes', False):
            print('The following keys are going to be deleted:')
            salt.output.display_output(
                    matches,
                    'key',
                    self.opts)
            try:
                veri = raw_input('Proceed? [N/y] ')
            except KeyboardInterrupt:
                raise SystemExit("\nExiting on CTRL-c")
            if veri.lower().startswith('y'):
                _print_deleted(matches, self.key.delete_key(match))
        else:
            print('Deleting the following keys:')
            salt.output.display_output(
                    matches,
                    'key',
                    self.opts)
            _print_deleted(matches, self.key.delete_key(match))