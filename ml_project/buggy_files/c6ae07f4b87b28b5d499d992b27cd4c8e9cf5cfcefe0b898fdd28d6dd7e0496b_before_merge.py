    def add_binstar_token(url):
        clean_url, token = split_anaconda_token(url)
        if not token and context.add_anaconda_token:
            for binstar_url, token in iteritems(read_binstar_tokens()):
                if clean_url.startswith(binstar_url):
                    log.debug("Adding anaconda token for url <%s>", clean_url)
                    from conda.models.channel import Channel
                    channel = Channel(clean_url)
                    channel.token = token
                    return channel.url(with_credentials=True)
        return url