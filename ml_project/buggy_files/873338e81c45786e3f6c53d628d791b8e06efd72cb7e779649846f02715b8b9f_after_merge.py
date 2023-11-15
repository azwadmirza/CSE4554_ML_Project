    def _check_pub_data(self, pub_data, listen=True):
        '''
        Common checks on the pub_data data structure returned from running pub
        '''
        if pub_data == '':
            # Failed to authenticate, this could be a bunch of things
            raise EauthAuthenticationError(
                'Failed to authenticate! This is most likely because this '
                'user is not permitted to execute commands, but there is a '
                'small possibility that a disk error occurred (check '
                'disk/inode usage).'
            )

        # Failed to connect to the master and send the pub
        if 'error' in pub_data:
            print(pub_data['error'])
            log.debug('_check_pub_data() error: {0}'.format(pub_data['error']))
            return {}
        elif 'jid' not in pub_data:
            return {}
        if pub_data['jid'] == '0':
            print('Failed to connect to the Master, '
                  'is the Salt Master running?')
            return {}

        # If we order masters (via a syndic), don't short circuit if no minions
        # are found
        if not self.opts.get('order_masters'):
            # Check for no minions
            if not pub_data['minions']:
                print('No minions matched the target. '
                      'No command was sent, no jid was assigned.')
                return {}

        # don't install event subscription listeners when the request is async
        # and doesn't care. this is important as it will create event leaks otherwise
        if not listen:
            return pub_data

        if self.opts.get('order_masters'):
            self.event.subscribe('syndic/.*/{0}'.format(pub_data['jid']), 'regex')

        self.event.subscribe('salt/job/{0}'.format(pub_data['jid']))

        return pub_data