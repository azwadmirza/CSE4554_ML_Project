    def query_all(channels, subdirs, package_ref_or_match_spec):
        channel_urls = all_channel_urls(channels, subdirs=subdirs)

        executor = None
        try:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            executor = ThreadPoolExecutor(10)
            futures = (executor.submit(
                SubdirData(Channel(url)).query, package_ref_or_match_spec
            ) for url in channel_urls)
            return tuple(concat(future.result() for future in as_completed(futures)))
        except RuntimeError as e:  # pragma: no cover
            # concurrent.futures is only available in Python >= 3.2 or if futures is installed
            # RuntimeError is thrown if number of threads are limited by OS
            raise
        finally:
            if executor:
                executor.shutdown(wait=True)