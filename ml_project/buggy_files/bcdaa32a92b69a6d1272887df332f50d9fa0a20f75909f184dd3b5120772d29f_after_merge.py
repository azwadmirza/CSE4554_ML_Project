    def query_all(channels, subdirs, package_ref_or_match_spec):
        from .index import check_whitelist  # TODO: fix in-line import
        channel_urls = all_channel_urls(channels, subdirs=subdirs)
        check_whitelist(channel_urls)
        with ThreadLimitedThreadPoolExecutor() as executor:
            futures = (executor.submit(
                SubdirData(Channel(url)).query, package_ref_or_match_spec
            ) for url in channel_urls)
            return tuple(concat(future.result() for future in as_completed(futures)))