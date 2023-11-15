    def channel_str(rec):
        if 'schannel' in rec:
            return rec['schannel']
        if 'url' in rec:
            return url_channel(rec['url'])[1]
        if 'channel' in rec:
            return canonical_channel_name(rec['channel'])
        return '<unknown>'