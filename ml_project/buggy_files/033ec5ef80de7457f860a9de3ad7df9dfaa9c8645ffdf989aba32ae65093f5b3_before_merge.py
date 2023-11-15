    def from_string(cls, string, channel_override=NULL):
        string = text_type(string)

        if is_url(string) and channel_override == NULL:
            return cls.from_url(string)

        if string.endswith('@'):
            return cls(channel='@',
                       name=string,
                       version="",
                       build_string="",
                       build_number=0,
                       dist_name=string)

        REGEX_STR = (r'(?:([^\s\[\]]+)::)?'        # optional channel
                     r'([^\s\[\]]+)'               # 3.x dist
                     r'(?:\[([a-zA-Z0-9_-]+)\])?'  # with_features_depends
                     )
        channel, original_dist, w_f_d = re.search(REGEX_STR, string).groups()

        if original_dist.endswith(CONDA_TARBALL_EXTENSION):
            original_dist = original_dist[:-len(CONDA_TARBALL_EXTENSION)]

        if channel_override != NULL:
            channel = channel_override
        elif channel is None:
            channel = UNKNOWN_CHANNEL

        # enforce dist format
        dist_details = cls.parse_dist_name(original_dist)
        return cls(channel=channel,
                   name=dist_details.name,
                   version=dist_details.version,
                   build_string=dist_details.build_string,
                   build_number=dist_details.build_number,
                   dist_name=original_dist)