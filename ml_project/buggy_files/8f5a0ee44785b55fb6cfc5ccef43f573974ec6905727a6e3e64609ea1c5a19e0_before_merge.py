    def from_dist_str(cls, dist_str):
        parts = {}
        if dist_str.endswith(CONDA_PACKAGE_EXTENSION_V1):
            dist_str = dist_str[:-len(CONDA_PACKAGE_EXTENSION_V1)]
        if '::' in dist_str:
            channel_subdir_str, dist_str = dist_str.split("::", 1)
            if '/' in channel_subdir_str:
                channel_str, subdir = channel_subdir_str.split('/', 2)
                parts.update({
                    'channel': channel_str,
                    'subdir': subdir,
                })
            else:
                parts['channel'] = channel_subdir_str

        name, version, build = dist_str.rsplit('-', 2)
        parts.update({
            'name': name,
            'version': version,
            'build': build,
        })
        return cls(**parts)