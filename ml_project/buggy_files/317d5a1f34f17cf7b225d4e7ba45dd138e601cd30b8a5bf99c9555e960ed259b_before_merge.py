    def _get_items(self):
        # TODO: Include .tar.bz2 files for local installs.
        from conda.core.index import get_index
        args = self.parsed_args
        call_dict = dict(channel_urls=args.channel or (),
                         use_cache=True,
                         prepend=not args.override_channels,
                         unknown=args.unknown)
        if hasattr(args, 'platform'):  # in search
            call_dict['platform'] = args.platform
        index = get_index(**call_dict)
        return [record.name for record in index]