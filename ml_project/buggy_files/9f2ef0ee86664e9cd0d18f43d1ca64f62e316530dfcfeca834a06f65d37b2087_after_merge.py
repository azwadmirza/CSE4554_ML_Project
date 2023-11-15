    def __init__(self, index, sort=False, processed=False):
        self.index = index
        if not processed:
            for fkey, info in iteritems(index.copy()):
                if fkey.endswith(']'):
                    continue
                for fstr in chain(info.get('features', '').split(),
                                  info.get('track_features', '').split(),
                                  track_features or ()):
                    self.add_feature(fstr, group=False)
                for fstr in iterkeys(info.get('with_features_depends', {})):
                    index['%s[%s]' % (fkey, fstr)] = info
                    self.add_feature(fstr, group=False)

        groups = {}
        trackers = {}
        installed = set()
        for fkey, info in iteritems(index):
            groups.setdefault(info['name'], []).append(fkey)
            for feat in info.get('track_features', '').split():
                trackers.setdefault(feat, []).append(fkey)
            if 'link' in info and not fkey.endswith(']'):
                installed.add(fkey)

        self.groups = groups
        self.installed = installed
        self.trackers = trackers
        self.find_matches_ = {}
        self.ms_depends_ = {}

        if sort:
            for name, group in iteritems(groups):
                groups[name] = sorted(group, key=self.version_key, reverse=True)