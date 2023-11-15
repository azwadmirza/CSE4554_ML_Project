    def channel_str(rec):
        if rec.get('schannel'):
            return rec['schannel']
        if rec.get('url'):
            return url_channel(rec['url'])[1]
        if rec.get('channel'):
            return canonical_channel_name(rec['channel'])
        return '<unknown>'