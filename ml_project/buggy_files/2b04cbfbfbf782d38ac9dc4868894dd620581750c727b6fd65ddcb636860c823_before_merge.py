    def _mixin_setup(self):
        # XXX: Remove '--key-logfile' support in 0.18.0
        utils.warn_until((0, 18), '', _dont_call_warnings=True)
        self.logging_options_group.add_option(
            '--key-logfile',
            default=None,
            help='Send all output to a file. Default is {0!r}'.format(
                self._default_logging_logfile_
            )
        )

        actions_group = optparse.OptionGroup(self, 'Actions')
        actions_group.add_option(
            '-l', '--list',
            default='',
            metavar='ARG',
            help=('List the public keys. The args '
                  '"pre", "un", and "unaccepted" will list '
                  'unaccepted/unsigned keys. '
                  '"acc" or "accepted" will list accepted/signed keys. '
                  '"rej" or "rejected" will list rejected keys. '
                  'Finally, "all" will list all keys.')
        )

        actions_group.add_option(
            '-L', '--list-all',
            default=False,
            action='store_true',
            help='List all public keys. Deprecated: use "--list all"'
        )

        actions_group.add_option(
            '-a', '--accept',
            default='',
            help='Accept the specified public key (use --include-all to '
                 'match rejected keys in addition to pending keys)'
        )

        actions_group.add_option(
            '-A', '--accept-all',
            default=False,
            action='store_true',
            help='Accept all pending keys'
        )

        actions_group.add_option(
            '-r', '--reject',
            default='',
            help='Reject the specified public key (use --include-all to '
                 'match accepted keys in addition to pending keys)'
        )

        actions_group.add_option(
            '-R', '--reject-all',
            default=False,
            action='store_true',
            help='Reject all pending keys'
        )

        actions_group.add_option(
            '--include-all',
            default=False,
            action='store_true',
            help='Include non-pending keys when accepting/rejecting'
        )

        actions_group.add_option(
            '-p', '--print',
            default='',
            help='Print the specified public key'
        )

        actions_group.add_option(
            '-P', '--print-all',
            default=False,
            action='store_true',
            help='Print all public keys'
        )

        actions_group.add_option(
            '-d', '--delete',
            default='',
            help='Delete the named key'
        )

        actions_group.add_option(
            '-D', '--delete-all',
            default=False,
            action='store_true',
            help='Delete all keys'
        )

        actions_group.add_option(
            '-f', '--finger',
            default='',
            help='Print the named key\'s fingerprint'
        )

        actions_group.add_option(
            '-F', '--finger-all',
            default=False,
            action='store_true',
            help='Print all key\'s fingerprints'
        )
        self.add_option_group(actions_group)

        self.add_option(
            '-q', '--quiet',
            default=False,
            action='store_true',
            help='Suppress output'
        )

        self.add_option(
            '-y', '--yes',
            default=False,
            action='store_true',
            help='Answer Yes to all questions presented, defaults to False'
        )

        key_options_group = optparse.OptionGroup(
            self, 'Key Generation Options'
        )
        self.add_option_group(key_options_group)
        key_options_group.add_option(
            '--gen-keys',
            default='',
            help='Set a name to generate a keypair for use with salt'
        )

        key_options_group.add_option(
            '--gen-keys-dir',
            default='.',
            help=('Set the directory to save the generated keypair, only '
                  'works with "gen_keys_dir" option; default=.')
        )

        key_options_group.add_option(
            '--keysize',
            default=2048,
            type=int,
            help=('Set the keysize for the generated key, only works with '
                  'the "--gen-keys" option, the key size must be 2048 or '
                  'higher, otherwise it will be rounded up to 2048; '
                  '; default=%default')
        )